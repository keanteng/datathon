import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
#import ssl

import warnings
warnings.filterwarnings('ignore')

# download nltk packages
nltk.download("punkt")
nltk.download("stopwords")

import streamlit as st

qualification_data = pd.read_excel("data/qualification level.xlsx")
sectors_data = pd.read_excel("data/skill by sector.xlsx")
course_suggestions_data = pd.read_excel("data/course suggestion.xlsx")

# Load qualification data from the "qualification level" Excel file
qualification_dict = dict(zip(qualification_data["qualification"], qualification_data["mqf level"]))

def preprocess_text(text):
    # lower case everything
    token = text.lower()   
    # tokenize 
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalnum()]
    # remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]
    return " ".join(tokens)

def compare_skills(user_skills, sector_skills):
    # preprocess text
    user_skills = preprocess_text(user_skills)
    sector_skills = preprocess_text(sector_skills)

    # vectorize text and calculate cosine similarity
    vectorizer = TfidfVectorizer(stop_words="english", analyzer="word")
    tfidf_matrix = vectorizer.fit_transform([user_skills, sector_skills])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

    return cosine_sim[0][0]


user_skills = "English, Leadership, Problem Solving, Malay, planning"
user_qualification = 6
user_sector = "Teacher"

matching_sectors = []

for _, row in sectors_data.iterrows():
    sector = row["sector"]
    sector_skills = row["skills"]
    min_qualification = row["qualification"]
    # compute the similarity score between user skills and all sector skills
    similarity_score = compare_skills(user_skills, sector_skills)
    
    # check if the similarity score is above 0 and if the user's qualification is above the minimum qualification level
    if similarity_score > 0 and int(user_qualification) >= int(min_qualification):
        if not user_sector or user_sector.lower() in sector.lower():
            matching_sectors.append(sector)

# output the results
if matching_sectors:
    # the matches sector could be more than one, so we need to loop through all of them
    for sector in matching_sectors:
        sector_row = sectors_data.loc[sectors_data["sector"] == sector].iloc[0]
        required_skills = set(sector_row["skills"].split(","))
        user_input_skills = set(user_skills.lower().split(","))
        matching_skills = user_input_skills.intersection(required_skills)
        lacking_skills = required_skills.difference(user_input_skills)

        print(f"Sector: {sector.title()}")
        print("Matching Skills:", ", ".join(matching_skills).title())
        print("Lacking Skills:", ", ".join(lacking_skills)[2:].title())
        print(f"Minimum Qualification: MQF Level {sector_row['qualification']}")
        
        course_suggestions = course_suggestions_data.loc[course_suggestions_data['sector'] == sector]
        if not course_suggestions.empty:
            print("Course Suggestions:")
            #display(course_suggestions)
            for _, suggestion_row in course_suggestions.iterrows():
                suggestion_row = pd.DataFrame(suggestion_row).transpose().reset_index(drop=True)
                #st.table(suggestion_row)
                
                text1 = str(suggestion_row['course suggestion 1'][0])
                suggestion_link1 = f"<a href='{suggestion_row['link_1'][0]}'>{text1}</a>"
                text2 = str(suggestion_row['course suggestion 2'][0])
                suggestion_link2 = f"<a href='{suggestion_row['link_2'][0]}'>{text2}</a>"
                text3 = str(suggestion_row['course suggestion 3'][0])
                suggestion_link3 = f"<a href='{suggestion_row['link_3'][0]}'>{text3}</a>"
                print(f"- {suggestion_link1}")
                st.markdown("- " + suggestion_link1, unsafe_allow_html=True)
                st.markdown(suggestion_link2, unsafe_allow_html=True)
                st.markdown(suggestion_link3, unsafe_allow_html=True)
                
                #for col in course_suggestions.columns[1:]:
                    #suggestion = suggestion_row[col]
                    #print(col) # column name
                    #suggestion_link = f"<a href='{suggestion}'>{col}</a>"
                    #print(f"- {suggestion_link}")


        if len(lacking_skills) > 0:
            print("Job Description:")
            job_description = sector_row["job description"].split(";")
            for desc in job_description:
                print(desc.strip())
# if no match found, output this message
else:
    print("Sorry, no matching sectors found in our database for your skills and qualification level.")