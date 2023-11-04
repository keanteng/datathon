# load packages
import pandas as pd
import numpy as np
import streamlit as st
import geopandas as gpd
from backend.functions import *
try:
    from backend.configs import *
except ImportError:
    pass
import matplotlib.pyplot as plt
from datetime import *
import google.generativeai as palm

# website settings
# turn off the side bar by default
st.set_page_config(layout="wide", initial_sidebar_state="auto")

## customize the side bar
st.sidebar.title("🌍 Geo-Sustainable Jobs Solution")
st.sidebar.caption("A Job Solution Prototype")

# user input
with st.sidebar:
    api_input = st.text_input("Enter Google API Key:", "Your API Key Here")
    location_input = st.text_input(
        "Enter a location (Malaysia Only):", "University Malaya"
    )
    state_input = st.selectbox(
        "Select a state:",
        [
            "W.P Kuala Lumpur",
            "Johor",
            "Kedah",
            "Kelantan",
            "Melaka",
            "Negeri Sembilan",
            "Pahang",
            "Perak",
            "Perlis",
            "Pulau Pinang",
            "Sabah",
            "Sarawak",
            "Selangor",
            "Terengganu",
            "W.P Labuan",
            "W.P Putrajaya",
        ],
    )
    # add exapander
    with st.expander("Your Job Profile", expanded=False):
        user_skills = st.text_input(
            "Enter Your Skills, Desired Sector & Qualifications:",
            "English, Leadership, Problem Solving, Malay, Program Planning",
        )
        user_qualification = st.selectbox(
            "Enter Your Qualification:",
            (
                "1-Skill Certificate 1",
                "2-Skill Certificate 2",
                "3-Skill Certificate 3",
                "4-Diploma",
                "5-Advanced Diploma",
                "6-Bachelor Degree",
                "7-Master Degree",
                "8-Doctorate Degree",
            ),
        )
        user_sector = st.text_input("Enter Your Desired Sector:", "Teacher")

    submit = st.button("Compute", type="primary")
    st.subheader("📈 OpenDOSM Statistics")
    st.caption("Source: Labour Market Review, 2023 Q2")

# setup the layout with columns
col1, col2 = st.columns(spec=[0.7, 0.3], gap="small")

# load data
df = gpd.read_file("data/shapefile/polbnda_mys.shp")
jobdata = pd.read_csv("data/job_posting_cleaned.csv")
dosm_supply = pd.ExcelFile("data/dosm_supply.xlsx")
dosm_demand = pd.ExcelFile("data/dosm_demand.xlsx")
airports = gpd.read_file("data/airports/hotosm_mys_airports_polygons.shp")
edu_fac = gpd.read_file(
    "data/edu_facilities/hotosm_mys_education_facilities_polygons.shp"
)
financial = gpd.read_file(
    "data/financial_service/hotosm_mys_financial_services_polygons.shp"
)
health = gpd.read_file(
    "data/health_facilities/hotosm_mys_health_facilities_polygons.shp"
)
point_of_interest = gpd.read_file(
    "data/point_of_interest/hotosm_mys_points_of_interest_polygons.shp"
)
seaports = gpd.read_file("data/sea_ports/hotosm_mys_sea_ports_polygons.shp")
qualification_data = pd.read_excel("data/qualification level.xlsx")
sectors_data = pd.read_excel("data/skill by sector.xlsx")
course_suggestions_data = pd.read_excel("data/course suggestion.xlsx")
vacancy_rate = pd.read_csv("data/Vacancy Rate.csv", index_col=[0], parse_dates=[0])
unemployment_rate = pd.read_csv("data/Unemployment Rate.csv")

# configure geodataframe
airports = gpd.GeoDataFrame(airports, geometry=airports.geometry, crs="EPSG:4326")
edu_fac = gpd.GeoDataFrame(edu_fac, geometry=edu_fac.geometry, crs="EPSG:4326")
financial = gpd.GeoDataFrame(financial, geometry=financial.geometry, crs="EPSG:4326")
health = gpd.GeoDataFrame(health, geometry=health.geometry, crs="EPSG:4326")
point_of_interest = gpd.GeoDataFrame(
    point_of_interest, geometry=point_of_interest.geometry, crs="EPSG:4326"
)
seaports = gpd.GeoDataFrame(seaports, geometry=seaports.geometry, crs="EPSG:4326")

# tidy up the data
airports = airports[["name", "aeroway", "geometry"]]
edu_fac = edu_fac[["name", "amenity", "geometry"]]
financial = financial[["name", "amenity", "geometry"]]
health = health[["healthcare", "name", "amenity", "geometry"]]
point_of_interest = point_of_interest[
    ["tourism", "name", "amenity", "shop", "geometry"]
]
seaports = seaports[["name", "amenity", "geometry"]]
vacancy_rate = vacancy_rate.dropna(axis=1, how="all")
vacancy_rate.dropna(inplace=True)
unemployment_rate = unemployment_rate.dropna(axis=1, how="all")

# change the type of vacancy_rate_employment as data frame
unemployment_rate = pd.DataFrame(unemployment_rate)
unemployment_rate.iloc[:, 1:] = unemployment_rate.iloc[:, 1:].astype(float)
unemployment_rate.iloc[:, 0] = pd.to_datetime(unemployment_rate.iloc[:, 0])
unemployment_rate = unemployment_rate.set_index("Date")

# temp map display
placeholder = st.empty()
with placeholder.container():
    m = leafmap.Map(center=[3.8, 101.4], zoom=7, google_map="HYBRID")
    m.to_streamlit(height=700)


##############################
# forecast engine
def dateofforecast(data):
    forecast_date = [
        "2023-04-01",
        "2023-07-01",
        "2023-10-01",
        "2024-01-01",
        "2024-04-01",
        "2024-07-01",
        "2024-10-01",
        "2025-01-01",
    ]
    forecast_date = pd.to_datetime(forecast_date)
    data.index = forecast_date


# ETS prediction
VETS_Kedah = ets_fore_a(vacancy_rate["Kedah"], 6)
VETS_Melaka = ets_fore_a(vacancy_rate["Melaka"], 6)
VETS_Negeri_Sembilan = ets_fore_c(vacancy_rate["Negeri Sembilan"], 6)
VETS_Pahang = ets_fore_a(vacancy_rate["Pahang"], 6)
VETS_Perlis = ets_fore_c(vacancy_rate["Perlis"], 6)
VETS_Terengganu = ets_fore_a(vacancy_rate["Terengganu"], 6)
VETS_Sabah = ets_fore_a(vacancy_rate["Sabah"], 6)
VETS_Sarawak = ets_fore_a(vacancy_rate["Sarawak"], 6)
VETS_Putrajaya = ets_fore_a(vacancy_rate["W.P Putrajaya"], 6)

# ARIMA prediction
VETS_Johor = ARIMA_fore(vacancy_rate["Johor"])
VETS_Kelantan = ARIMA_fore(vacancy_rate["Kelantan"])
VETS_Penang = ARIMA_fore(vacancy_rate["Pulau Pinang"])
VETS_Perak = ARIMA_fore(vacancy_rate["Perak"])
VETS_Selangor = ARIMA_fore(vacancy_rate["Selangor"])
VETS_Kuala_Lumpur = ARIMA_fore(vacancy_rate["W.P Kuala Lumpur"])
VETS_Labuan = ARIMA_fore(vacancy_rate["W.P Labuan"])
VETS_Total = ARIMA_fore(vacancy_rate["Total"])

# Change the Starting date of the forecast
dateofforecast(VETS_Kedah)
dateofforecast(VETS_Melaka)
dateofforecast(VETS_Negeri_Sembilan)
dateofforecast(VETS_Pahang)
dateofforecast(VETS_Perlis)
dateofforecast(VETS_Terengganu)
dateofforecast(VETS_Sabah)
dateofforecast(VETS_Sarawak)
dateofforecast(VETS_Putrajaya)
dateofforecast(VETS_Johor)
dateofforecast(VETS_Kelantan)
dateofforecast(VETS_Penang)
dateofforecast(VETS_Perak)
dateofforecast(VETS_Selangor)
dateofforecast(VETS_Kuala_Lumpur)
dateofforecast(VETS_Labuan)
dateofforecast(VETS_Total)

# ETS Model
Johor_vpred = ets_fore_a(unemployment_rate[["Johor"]], 6)
Kedah_pred = ets_fore_d(unemployment_rate[["Kedah"]], 6)
Kelantan_pred = ets_fore_d(unemployment_rate[["Kelantan"]], 6)
Melaka_pred = ets_fore_b(unemployment_rate[["Melaka"]], 6)
Pahang_pred = ets_fore_c(unemployment_rate[["Pahang"]], 6)
Perak_pred = ets_fore_c(unemployment_rate[["Perak"]], 6)
Perlis_pred = ets_fore_c(unemployment_rate[["Perlis"]], 6)
Sabah_pred = ets_fore_a(unemployment_rate[["Sabah"]], 6)
Sarawak_pred = ets_fore_d(unemployment_rate[["Sarawak"]], 6)
Selangor_pred = ets_fore_d(unemployment_rate[["Selangor"]], 6)
Terengganu_pred = ets_fore_b(unemployment_rate[["Terengganu"]], 6)
Labuan_pred = ets_fore_d(unemployment_rate["W.P Labuan"], 6)

# ARIMA Model
UARIMA_N9_pred = ARIMA_fore(unemployment_rate[["Negeri Sembilan"]])
UARIMA_Penang_pred = ARIMA_fore(unemployment_rate[["Pulau Pinang"]])
UARIMA_KL_pred = ARIMA_fore(unemployment_rate[["W.P Kuala Lumpur"]])
UARIMA_Putrajaya_pred = ARIMA_fore(unemployment_rate[["W.P Putrajaya"]])
UARIMA_Malaysia_pred = ARIMA_fore(unemployment_rate[["Total"]])

# Change the Starting date of the forecast
dateofforecast(Johor_vpred)
dateofforecast(Kedah_pred)
dateofforecast(Kelantan_pred)
dateofforecast(Melaka_pred)
dateofforecast(Pahang_pred)
dateofforecast(Perak_pred)
dateofforecast(Perlis_pred)
dateofforecast(Sabah_pred)
dateofforecast(Sarawak_pred)
dateofforecast(Selangor_pred)
dateofforecast(Terengganu_pred)
dateofforecast(Labuan_pred)
dateofforecast(UARIMA_N9_pred)
dateofforecast(UARIMA_Penang_pred)
dateofforecast(UARIMA_KL_pred)
dateofforecast(UARIMA_Putrajaya_pred)
dateofforecast(UARIMA_Malaysia_pred)

vacancy_rate.dateformat = vacancy_rate.index.strftime("%Y-%m-%d")
unemployment_rate.dateformat = unemployment_rate.index.strftime("%Y-%d-%m")
plt.rcParams["figure.figsize"] = (20, 12)


def forecast_plot(state):
    state = state.title()
    if state == "Kedah":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Kedah"], label="Vacancy Rate")
        ax1.plot(VETS_Kedah, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Kedah"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Kedah_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Johor":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Johor"], label="Vacancy Rate")
        ax1.plot(VETS_Johor, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Johor"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Johor_vpred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Kelantan":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Kelantan"], label="Vacancy Rate")
        ax1.plot(VETS_Kelantan, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Kelantan"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Kelantan_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Melaka":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Melaka"], label="Vacancy Rate")
        ax1.plot(VETS_Melaka, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Melaka"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Melaka_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Negeri Sembilan":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(
            vacancy_rate.index, vacancy_rate["Negeri Sembilan"], label="Vacancy Rate"
        )
        ax1.plot(VETS_Negeri_Sembilan, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Negeri Sembilan"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(UARIMA_N9_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Pahang":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Pahang"], label="Vacancy Rate")
        ax1.plot(VETS_Pahang, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Pahang"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Pahang_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Penang":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Pulau Pinang"], label="Vacancy Rate")
        ax1.plot(VETS_Penang, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Pulau Pinang"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(UARIMA_Penang_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Perak":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Perak"], label="Vacancy Rate")
        ax1.plot(VETS_Perak, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Perak"],
            "r",
            label="Unemployment Rate",
        )
        ax2.plot(Perak_pred, "b", label="Forecast of Unemployment Rate")
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Perlis":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Perlis"], label="Vacancy Rate")
        ax1.plot(VETS_Perlis, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Perlis_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Perlis"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Sabah":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Sabah"], label="Vacancy Rate")
        ax1.plot(VETS_Sabah, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Sabah_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Sabah"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Sarawak":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Sarawak"], label="Vacancy Rate")
        ax1.plot(VETS_Sarawak, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Sarawak_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Sarawak"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Selangor":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Selangor"], label="Vacancy Rate")
        ax1.plot(VETS_Selangor, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Selangor_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Selangor"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Terengganu":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["Terengganu"], label="Vacancy Rate")
        ax1.plot(VETS_Terengganu, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Terengganu_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Terengganu"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "W.P Kuala Lumpur":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(
            vacancy_rate.index, vacancy_rate["W.P Kuala Lumpur"], label="Vacancy Rate"
        )
        ax1.plot(VETS_Kuala_Lumpur, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(UARIMA_KL_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["W.P Kuala Lumpur"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "W.P Labuan":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(vacancy_rate.index, vacancy_rate["W.P Labuan"], label="Vacancy Rate")
        ax1.plot(VETS_Labuan, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(Labuan_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["W.P Labuan"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "W.P Putrajaya":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(12, 8))

        ax1.plot(
            vacancy_rate.index, vacancy_rate["W.P Putrajaya"], label="Vacancy Rate"
        )
        ax1.plot(VETS_Putrajaya, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(UARIMA_Putrajaya_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["W.P Putrajaya"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)

    elif state == "Malaysia":
        fig, ax1 = plt.subplots()
        plt.figure(figsize=(20, 12))

        ax1.plot(vacancy_rate.index, vacancy_rate["Total"], label="Vacancy Rate")
        ax1.plot(VETS_Total, label="Forecast of Vacancy Rate")
        ax1.legend(loc="upper left")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Vacancy Rate")

        ax2 = ax1.twinx()
        ax2.plot(UARIMA_Malaysia_pred, "b", label="Forecast of Unemployment Rate")
        ax2.plot(
            unemployment_rate.index,
            unemployment_rate["Total"],
            "r",
            label="Unemployment Rate",
        )
        ax2.legend(loc="upper left", bbox_to_anchor=(0, 0.95))
        ax2.set_ylabel("Unemployment Rate")
        plt.rcParams["figure.figsize"] = (20, 12)
        st.pyplot(fig)


#############################

# visualization part for the selected state
if state_input:
    with st.sidebar:
        with st.expander("Vacancy & Unemployment Rate (%) Projection", expanded=False):
            forecast_plot(state_input)
        with st.expander("State Labour Supply ('000)", expanded=False):
            supply_state = dosm_supply.parse("state")
            supply_state = supply_state[supply_state["state"] == state_input]
            st.dataframe(supply_state, hide_index=True)
        with st.expander("By Ethnic Group ('000)", expanded=False):
            ethnic_state = dosm_supply.parse("ethnic")
            st.dataframe(ethnic_state, hide_index=True)
        with st.expander("By Age Group ('000)", expanded=False):
            age_state = dosm_supply.parse("age")
            st.dataframe(age_state, hide_index=True)
        with st.expander("By Education Level ('000)", expanded=False):
            edu_state = dosm_supply.parse("edu")
            st.dataframe(edu_state, hide_index=True)
        with st.expander("Vacancy Ads Count", expanded=False):
            vacancy_ads_state = dosm_demand.parse("vacancy_ads_state")
            vacancy_ads_state = vacancy_ads_state[
                vacancy_ads_state["state"] == state_input
            ]
            st.dataframe(vacancy_ads_state, hide_index=True)
        with st.expander("Sector Performance", expanded=False):
            sector_wage_prob = dosm_demand.parse("sector_wage_prob")
            st.dataframe(sector_wage_prob, hide_index=True)

# submit button is clicked
if submit:
    # clear the map
    placeholder.empty()
    with st.spinner("Hang on for a second..."):
        with col1:
            ## map generation
            input_df = geocoder(location_input)

            if input_df["Latitude"][0] == None:
                st.error("Location not found. Please try again.")
                st.stop()

            intersected_df = intersection_check(input_df, df)

            m = leafmap.Map(
                center=[input_df["Latitude"][0], input_df["Longitude"][0]],
                zoom=15,
                google_map="HYBRID",
            )
            style = {
                "stroke": True,
                "color": "#0000ff",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#0000ff",
                "fillOpacity": 0.1,
            }
            style_extras = {
                "stroke": True,
                "color": "#d82c02",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#d82c02",
                "fillOpacity": 0.1,
            }

            m.add_points_from_xy(
                input_df,
                x="Longitude",
                y="Latitude",
                icon_names=["gear", "map", "leaf", "globe"],
            )
            m.add_gdf(intersected_df, layer_name="Region of Interest", style=style)
            m.add_gdf(df, layer_name="Region of Interest", style=style)
            m.add_gdf(airports, layer_name="Airports", style=style_extras)
            m.add_gdf(edu_fac, layer_name="Education Facilities", style=style_extras)
            m.add_gdf(financial, layer_name="Financial Services", style=style_extras)
            m.add_gdf(health, layer_name="Health Facilities", style=style_extras)
            m.add_gdf(
                point_of_interest, layer_name="Point of Interest", style=style_extras
            )
            m.add_gdf(seaports, layer_name="Sea Ports", style=style_extras)
            m.to_streamlit(height=700)

            st.sidebar.expander("ℹ️ About", expanded=True)

        with col2:
            # configure the API
            configure_api()
            
            # get the skill list
            skill_list = skill_suggest_model(location_input)
            # get the job list
            job_list = job_suggest_model(skill_list)

            # cleaning
            skill_list = list_cleaning(skill_list)
            job_list = list_cleaning(job_list)

            st.subheader("🧪 Skill List:")
            st.write(
                "Based on the location of interest, we suggest the following skills:"
                + " "
                + skill_list
            )

            st.divider()

            st.subheader("💼 Job List:")
            st.write(
                "Based on the skills, we suggest the following jobs:" + " " + job_list
            )

            # job recommendation engine
            job_list = job_list.split(", ")
            result_df = []

            for i in range(0, len(job_list)):
                job_match = job_matcher(
                    jobdata, column="title", string_to_match=str(job_list[i])
                )

                if job_match.empty:
                    continue
                else:
                    job_key = job_match["title"][0]

                    # result = job_recom_engine(jobdata, job_key=job_key)
                    sig = job_recom_engine(jobdata)
                    result = give_rec(
                        titlename=job_key, sig=sig, jobdata=jobdata
                    ).sort_values(by="View", ascending=False)
                    result_df.append(result)

            # if the result is empty we will return empty dataframe
            if len(result_df) == 0:
                pass
            else:
                result_df = pd.concat([df for df in result_df], ignore_index=True)

            with st.expander("Job Recommendation", expanded=False):
                st.table(result_df)

            # resume recommendation engine
            qualification_dict = dict(
                zip(
                    qualification_data["qualification"], qualification_data["mqf level"]
                )
            )
            matching_sectors = []

            for _, row in sectors_data.iterrows():
                sector = row["sector"]
                sector_skills = row["skills"]
                min_qualification = row["qualification"]
                # compute the similarity score between user skills and all sector skills
                similarity_score = compare_skills(user_skills, sector_skills)

                # check if the similarity score is above 0 and if the user's qualification is above the minimum qualification level
                if similarity_score > 0 and int(user_qualification[0:1]) >= int(
                    min_qualification
                ):
                    if not user_sector or user_sector.lower() in sector.lower():
                        matching_sectors.append(sector)

            # output the results
            with st.expander("Job Profile Analysis", expanded=False):
                if matching_sectors:
                    # the matches sector could be more than one, so we need to loop through all of them
                    for sector in matching_sectors:
                        sector_row = sectors_data.loc[
                            sectors_data["sector"] == sector
                        ].iloc[0]
                        required_skills = set(sector_row["skills"].split(","))
                        user_input_skills = set(user_skills.lower().split(","))
                        matching_skills = user_input_skills.intersection(
                            required_skills
                        )
                        lacking_skills = required_skills.difference(user_input_skills)

                        st.write(f"**Sector:** {sector.title()}")
                        st.write(
                            "**Matching Skills:**", ", ".join(matching_skills).title()
                        )
                        st.write(
                            "**Lacking Skills:**", ", ".join(lacking_skills)[2:].title()
                        )
                        st.write(
                            f"**Minimum Qualification:** MQF Level {sector_row['qualification']}"
                        )

                        course_suggestions = course_suggestions_data.loc[
                            course_suggestions_data["sector"] == sector
                        ]
                        if not course_suggestions.empty:
                            st.write("**Course Suggestions:**")

                            for _, suggestion_row in course_suggestions.iterrows():
                                suggestion_row = (
                                    pd.DataFrame(suggestion_row)
                                    .transpose()
                                    .reset_index(drop=True)
                                )

                                text1 = str(suggestion_row["course suggestion 1"][0])
                                suggestion_link1 = f"<a href='{suggestion_row['link_1'][0]}'>{text1}</a>"
                                text2 = str(suggestion_row["course suggestion 2"][0])
                                suggestion_link2 = f"<a href='{suggestion_row['link_2'][0]}'>{text2}</a>"
                                text3 = str(suggestion_row["course suggestion 3"][0])
                                suggestion_link3 = f"<a href='{suggestion_row['link_3'][0]}'>{text3}</a>"
                                st.markdown(
                                    "- " + suggestion_link1, unsafe_allow_html=True
                                )
                                st.markdown(
                                    "- " + suggestion_link2, unsafe_allow_html=True
                                )
                                st.markdown(
                                    "- " + suggestion_link3, unsafe_allow_html=True
                                )

                        if len(lacking_skills) > 0:
                            st.write("**Role & Responsibilities:**")
                            job_description = sector_row["job description"].split(";")
                            for desc in job_description:
                                st.write(desc.strip())
                        st.divider()
                # if no match found, output this message
                else:
                    st.write(
                        "Sorry, no matching sectors found in our database for your skills and qualification level."
                    )

            # regional analysis
            airport_count = []
            edu_fac_count = []
            financial_count = []
            health_count = []
            seaports_count = []

            intersected_df = intersected_df.reset_index()

            for index in range(len(airports)):
                if (
                    intersected_df["geometry"][0].contains(airports["geometry"][index])
                    == True
                ):
                    airport_count.append(airports["name"][index])
            for index in range(len(edu_fac)):
                if (
                    intersected_df["geometry"][0].contains(edu_fac["geometry"][index])
                    == True
                ):
                    edu_fac_count.append(edu_fac["name"][index])
            for index in range(len(financial)):
                if (
                    intersected_df["geometry"][0].contains(financial["geometry"][index])
                    == True
                ):
                    financial_count.append(financial["name"][index])
            for index in range(len(health)):
                if (
                    intersected_df["geometry"][0].contains(health["geometry"][index])
                    == True
                ):
                    health_count.append(health["name"][index])
            for index in range(len(seaports)):
                if (
                    intersected_df["geometry"][0].contains(seaports["geometry"][index])
                    == True
                ):
                    seaports_count.append(seaports["name"][index])

            poi_name = []
            poi_tourism = []
            poi_amenity = []
            poi_shop = []

            for index in range(len(point_of_interest)):
                if (
                    intersected_df["geometry"][0].contains(
                        point_of_interest["geometry"][index]
                    )
                    == True
                ):
                    poi_name.append(point_of_interest["name"][index])
                    poi_tourism.append(point_of_interest["tourism"][index])
                    poi_amenity.append(point_of_interest["amenity"][index])
                    poi_shop.append(point_of_interest["shop"][index])

            # make a
            poi = pd.DataFrame(
                {
                    "name": poi_name,
                    "Tourism": poi_tourism,
                    "Amenity": poi_amenity,
                    "Shop": poi_shop,
                }
            )

            # find the location of interest
            no_hotel = len(
                poi[(poi["Tourism"] == "hotel") | (poi["Tourism"] == "hostel")]
            )
            no_theme_park = len(poi[(poi["Tourism"] == "theme_park")])
            no_food_place = len(
                poi[
                    (poi["Amenity"] == "restaurant")
                    | (poi["Amenity"] == "cafe")
                    | (poi["Amenity"] == "fast_food")
                ]
            )
            no_fuel = len(poi[(poi["Amenity"] == "fuel")])
            no_marketplace = len(poi[poi["Shop"] == "marketplace"])
            no_supermarket = len(
                poi[(poi["Shop"] == "supermarket") | (poi["Shop"] == "convenience")]
            )
            no_cloth_jewelry = len(
                poi[(poi["Shop"] == "clothes") | (poi["Shop"] == "jewelry")]
            )
            no_mall = len(
                poi[(poi["Shop"] == "mall") | (poi["Shop"] == "department_store")]
            )
            no_repair = len(
                poi[(poi["Shop"] == "car_repair") | poi["Shop"] == "motorcycle"]
            )
            no_hair = len(poi[poi["Shop"] == "hairdresser"])
            no_telco = len(
                poi[
                    (poi["Shop"] == "telecommunication")
                    | (poi["Shop"] == "electronics")
                ]
            )

            # make a dataframe
            poi_df = pd.DataFrame(
                {
                    "Place": [
                        "Airport",
                        "Education Facilities",
                        "Financial Facilities",
                        "Health Facilities",
                        "Seaports",
                        "Hotel",
                        "Theme Park",
                        "Food Place",
                        "Fuel Station",
                        "Marketplace",
                        "Supermarket",
                        "Cloth & Jewelry",
                        "Mall",
                        "Repair Shops",
                        "Hair Salon",
                        "Telco",
                    ],
                    "Count": [
                        len(airport_count),
                        len(edu_fac_count),
                        len(financial_count),
                        len(health_count),
                        len(seaports),
                        no_hotel,
                        no_theme_park,
                        no_food_place,
                        no_fuel,
                        no_marketplace,
                        no_supermarket,
                        no_cloth_jewelry,
                        no_mall,
                        no_repair,
                        no_hair,
                        no_telco,
                    ],
                }
            )

            with st.sidebar:
                st.subheader("📍 Location Analysis")
                with st.expander("Point of Interest", expanded=False):
                    st.table(poi_df)

# sidebar footer
st.sidebar.caption(
    "MIT License 2023 © Isekai Truck: Ang Zhi Nuo, Connie Hui Kang Yi, Khor Kean Teng, Ling Sing Cheng, Tan Yu Jing"
)
