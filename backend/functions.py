import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from geopy.geocoders import Nominatim
import leafmap.foliumap as leafmap
from shapely.geometry import Polygon, MultiPolygon
import google.generativeai as palm
try:
    from backend.configs import *
except ImportError:
    pass
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
from sklearn.metrics.pairwise import cosine_similarity
import fuzzywuzzy
from fuzzywuzzy import process
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
nltk.download("punkt")
nltk.download("stopwords")

# forecasting
from datetime import *
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as ax1
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt


# convert to lat long
def geocoder(location_input):
    """
    Perform geocoding on location input. The input should be an address.

    Args:
        location_input (string): string input

    Returns:
        dataframe: a geodataframe with latitude and longitude and geometry
    """

    try:
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(location_input)

        location_df = pd.DataFrame(
            {
                "City": location_input,
                "Latitude": [location.latitude],
                "Longitude": [location.longitude],
            }
        )

        location_df = gpd.GeoDataFrame(
            location_df,
            geometry=gpd.points_from_xy(location_df.Longitude, location_df.Latitude),
        )

        return location_df

    except:
        location_df = pd.DataFrame(
            {
                "City": location_input,
                "Latitude": [None],
                "Longitude": [None],
            }
        )
        return location_df


# check intersection
def intersection_check(location_df, df):
    """
    Perform intersection check between location_df and df. The input should be a geodataframe.

    Args:
        location_df (geodataframe): a geodataframe, the location input of your choice
        df (geodataframe): a geodataframe, the shapefile of Malaysia

    Returns:
        geodataframe: a geodataframe with the intersected area. It contains the geometry and the state and district name.
    """

    for index in range(len(df)):
        if df["geometry"][index].contains(location_df["geometry"][0]) == True:
            df = df.loc[index, :].to_frame().transpose()
            df = df[["nam", "laa", "geometry"]]
            df = gpd.GeoDataFrame(df, geometry=df.geometry, crs="EPSG:4326")
            df.reset_index()
            df["geometry"] = MultiPolygon([df["geometry"].to_numpy()[0]])
            return df


# for testing
# df = gpd.read_file("data/shapefile/polbnda_mys.shp")
# a = intersection_check(geocoder('Johor Bahru'), df)
# print(a)


# palm model
# configure API
@st.cache_resource
def configure_api(token_name = "PALM_TOKEN"):
    """
    Configure the API key for palm model.
    """
    try:
        palm.configure(api_key=params["PALM_TOKEN"])
    except:
        palm.configure(api_key="PALM_TOKEN")


# generate palm model
def skill_suggest_model(location_input):
    """
    Suggest skills based on user location input.

    Args:
        location_input (string): a string, the location input of your choice

    Returns:
        list: a list of skills based on the location input
    """
    models = [
        m
        for m in palm.list_models()
        if "generateText" in m.supported_generation_methods
    ]
    model = models[0].name  # using text-bison-001

    text = """
    You will now only response by giving a list as such [element1, element2, element3, ...].

    You will be prompted with name of city around the world. For example,
    Example1: Paris

    You will then response with a list where each element in the list will either be a noun or an
    adjective. These words will describe the skills needed to work in that city. For example,

    Example1: Silicon Valley
    Answer: [programming, python, deep learning, web development]

    Please answer the following questions: 
    """

    prompt = text + "" + location_input

    # generate text
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
    )

    return completion.result


# testing
# configure_api()
# a = skill_suggest_model('Kuala Lumpur')
# print(a)


def job_suggest_model(skills_list):
    """
    Suggest jobs based on a list of skills.

    Args:
        list of skills (list): a list, the skills input of your choice

    Returns:
        list: a list of jobs based on the skills input
    """
    models = [
        m
        for m in palm.list_models()
        if "generateText" in m.supported_generation_methods
    ]
    model = models[0].name  # using text-bison-001

    text = """
    You will now only response by giving a list of only 3 elements as such [element1, element2, element3].

    You are an expert hiring manager. You will be prompted with skills related to a person job. For example,
    Example1: [finance, accounting, banking]

    You will then response with a list where each element is the possible job roles. For example,

    Example1: [finance, accounting, banking]
    Answer: [financial analyst, accountant, investmetn banking associate]

    Please answer the following questions: 
    """

    prompt = text + "" + skills_list

    # generate text
    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        # The maximum length of the response
        max_output_tokens=800,
    )

    return completion.result


# testing
# configure_api()
# skill = ['programming', 'python', 'deep learning', 'web development']
# a = job_suggest_model(str(skill))
# print(a)


def list_cleaning(list_input):
    """
    Remove first and last character of the string

    Args:
        string_input (string): a string

    Returns:
        string: a string with the first and last character removed
    """
    list_input = list_input[:-1]
    list_input = list_input[1:]

    return list_input


# job prediction model
# text cleaning
def text_cleaning(text):
    """
    Clean the text by removing special characters.

    Args:
        text (dataframe): a dataframe with text

    Returns:
        dataframe: a dataframe with text cleaned
    """
    text = re.sub(r"&quot;", "", text)
    text = re.sub(r".hack//", "", text)
    text = re.sub(r"&#039;", "", text)
    text = re.sub(r"A&#039;s", "", text)
    text = re.sub(r"I&#039;", "I'", text)
    text = re.sub(r"&amp;", "and", text)

    return text


# recommendation engine
def give_rec(titlename, sig, jobdata):
    """
    Give recommendation based on the job title.

    Args:
        titlename (string): a string, the job title of your choice
        sig (model): a model, the sigmoid kernel model
        jobdata (dataframe): a dataframe, the job posting dataset

    Returns:
        dataframe: a dataframe with the top 5 recommended jobs
    """
    # Get the index corresponding to original_title
    indices = pd.Series(jobdata.index, index=jobdata["title"]).drop_duplicates()
    indices_frame = pd.DataFrame(indices).reset_index().drop_duplicates(subset="title")

    # rename the columns
    indices_frame.columns = ["title", "views"]
    indices_frame["work type"] = jobdata["work_type"]
    indices_frame["location"] = jobdata["location"]

    # Get the index corresponding to original_title
    idx = indices_frame[indices_frame["title"] == titlename]["views"]
    idx = idx.index.to_numpy()[0]

    # Get the pairwsie similarity scores
    sig_scores = list(enumerate(sig[idx]))

    # Sort the movies
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)

    # Scores of the 10 most similar movies
    sig_scores = sig_scores[1:11]

    # Movie indices
    anime_indices = [i[0] for i in sig_scores]

    # Top 10 most similar movies
    return pd.DataFrame(
        {
            "Job Title": jobdata["title"].iloc[anime_indices].values,
            "View": jobdata["views"].iloc[anime_indices].values,
            "Work Type": jobdata["work_type"].iloc[anime_indices].values,
            "Location": jobdata["location"].iloc[anime_indices].values,
        }
    )


# job recommendation engine workflow
@st.cache_resource
def job_recom_engine(jobdata):
    """
    Job recommendation engine workflow.

    Args:
        jobdata (dataframe): a dataframe, the job posting dataset

    Returns:
        dataframe: a dataframe with the top 5 recommended jobs
    """
    # filter views less than 5
    jobdata = jobdata[jobdata["views"] >= 5]

    # data cleaning
    jobdata["description"] = jobdata["description"].apply(text_cleaning)
    jobdata["tokenized_Description"] = jobdata["tokenized_Description"].apply(
        text_cleaning
    )

    # load model
    tfv = TfidfVectorizer(
        min_df=3,
        max_features=None,
        strip_accents="unicode",
        analyzer="word",
        token_pattern=r"\w{1,}",
        ngram_range=(1, 3),
        stop_words="english",
    )

    # Filling NaNs with empty string
    jobdata["tokenized_Description"] = jobdata["tokenized_Description"].fillna("")
    genres_str = jobdata["tokenized_Description"].str.split(",").astype(str)
    tfv_matrix = tfv.fit_transform(genres_str)

    # sigmoid kernel
    sig = sigmoid_kernel(tfv_matrix, tfv_matrix)

    # recommended_jobs = (
    # give_rec(titlename=job_key, sig=sig, jobdata=jobdata)
    # .sort_values(by="View", ascending=False)
    # )

    return sig


# testing
# jobdata = pd.read_csv('data/job_posting_clean.csv')
# a = job_recom_engine(jobdata, 'Data Scientist')
# print(a)


# fuzzy matching
def job_matcher(jobdata, column="title", string_to_match=None, min_ratio=85):
    # get a list of unique strings
    jobdata = jobdata[jobdata["views"] >= 5]
    strings = jobdata[column].unique()

    # get the top 10 closest matches to our input string
    matches = fuzzywuzzy.process.extract(
        string_to_match,
        strings,
        limit=10,
        scorer=fuzzywuzzy.fuzz.token_sort_ratio,
    )

    # only get matches with a ratio > 88
    close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]

    # get the rows of all the close matches in our dataframe
    rows_with_matches = jobdata[column].isin(close_matches)

    match_data = jobdata.loc[rows_with_matches]["title"]

    return match_data.to_frame().head().reset_index()


# testing
# jobdata = pd.read_csv('data/job_posting_clean.csv')
# a = job_matcher(jobdata = jobdata, column = 'title', string_to_match = 'financial analyst')
# print(a['title'][0])


# resume analysis model
def preprocess_text(text_input):
    """
    Preprocess text by removing special characters, stop words, and stemming.

    Args:
        text_input (string): a string, the text input of your choice

    Returns:
        string: a string with the special characters, stop words, and stemming removed
    """
    tokens = text_input.lower()
    tokens = word_tokenize(tokens)
    tokens = [word.lower() for word in tokens if word.isalnum()]

    # remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if not word in stop_words]
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]

    return " ".join(tokens)


def compare_skills(user_skills, sector_skills):
    """
    Compare skills between user and sector.

    Args:
        user_skills (string): a string, the user skills input of your choice
        sector_skills (string): a string, the sector skills input of your choice

    Returns:
        numeric: a numeric value, the cosine similarity between the user and sector skills
    """
    # preprocess text
    user_skills = preprocess_text(user_skills)
    sector_skills = preprocess_text(sector_skills)

    # vectorize text and calculate cosine similarity
    vectorizer = TfidfVectorizer(stop_words="english", analyzer="word")
    tfidf_matrix = vectorizer.fit_transform([user_skills, sector_skills])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    return cosine_sim[0][0]


# forecasting model
def ets_fore_a(data, i):
    # ets test
    ets_model = ExponentialSmoothing(
        data, trend="add", seasonal="add", seasonal_periods=i
    )
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred


def ets_fore_b(data, i):
    # ets test
    ets_model = ExponentialSmoothing(
        data, trend="add", seasonal="mul", seasonal_periods=i
    )
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred


def ets_fore_c(data, i):
    # ets test
    ets_model = ExponentialSmoothing(
        data, trend="mul", seasonal="add", seasonal_periods=i
    )
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred


def ets_fore_d(data, i):
    # ets test
    ets_model = ExponentialSmoothing(
        data, trend="mul", seasonal="mul", seasonal_periods=i
    )
    ets_model_fit = ets_model.fit()
    ets_pred = ets_model_fit.forecast(8)
    return ets_pred


def ARIMA_fore(data):
    # arima test
    stepwise_model = auto_arima(data, start_p=1, start_q=1, stepwise=True)
    stepwise_model.fit(data)
    arima_pred = stepwise_model.predict(n_periods=8)
    return arima_pred
