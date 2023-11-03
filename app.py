# load packages
import pandas as pd
import numpy as np
import streamlit as st
import geopandas as gpd
from backend.functions import *
from backend.config import *

# website settings
# turn off the side bar by default
st.set_page_config(layout="wide", initial_sidebar_state="auto")

## customize the side bar
st.sidebar.title("🌍 Geo-Sustainable Jobs Solution")
st.sidebar.caption("A Solution Prototype")

# user input 
with st.sidebar:
    location_input = st.text_input("Enter a location of interest:", "Kuala Lumpur Sentral")
    state_input = st.selectbox("Select a state:", 
        ["W.P Kuala Lumpur", "Johor", "Kedah", "Kelantan", "Melaka", 
         "Negeri Sembilan", "Pahang", "Perak", "Perlis", 
         "Pulau Pinang", "Sabah", "Sarawak", "Selangor", 
         "Terengganu", "W.P Labuan", "W.P Putrajaya"])
    submit = st.button("Compute", type = 'primary')
    st.subheader("📈 OpenDOSM Statistics")

# setup the layout with columns
col1, col2 = st.columns(spec = [0.7, 0.3], gap = 'small')

# load data
df = gpd.read_file("data/shapefile/polbnda_mys.shp")
jobdata = pd.read_csv('data/job_posting_clean.csv')
dosm_supply = pd.ExcelFile('data/dosm_supply.xlsx')
dosm_demand = pd.ExcelFile('data/dosm_demand.xlsx')

# temp map display
placeholder = st.empty()
with placeholder.container():
    m = leafmap.Map(center = [3.8, 101.4], zoom = 7, google_map = "HYBRID")
    m.to_streamlit(height=700)
    
# visualization part for the selected state
if state_input:
    with st.sidebar:
        with st.expander("State Labour Supply ('000)", expanded = False):
            supply_state = dosm_supply.parse("state")
            supply_state = supply_state[supply_state['state'] == state_input]
            st.dataframe(supply_state, hide_index=True)
        with st.expander("By Ethnic Group ('000)", expanded=False):
            ethnic_state = dosm_supply.parse('ethnic')
            st.dataframe(ethnic_state, hide_index=True)
        with st.expander("By Age Group ('000)", expanded=False):
            age_state = dosm_supply.parse('age')
            st.dataframe(age_state, hide_index=True)
        with st.expander("By Education Level ('000)", expanded=False):
            edu_state = dosm_supply.parse('edu')
            st.dataframe(edu_state, hide_index=True)
        with st.expander("Vacancy Ads Count", expanded=False):
            vacancy_ads_state = dosm_demand.parse('vacancy_ads_state')
            vacancy_ads_state = vacancy_ads_state[vacancy_ads_state['state'] == state_input]
            st.dataframe(vacancy_ads_state, hide_index=True)
        with st.expander("Sector Performance", expanded=False):
            sector_wage_prob = dosm_demand.parse('sector_wage_prob')
            st.dataframe(sector_wage_prob, hide_index=True)

# submit button is clicked
if submit:
    # clear the map
    placeholder.empty()
    with st.spinner():
        with col1:
            ## map generation
            input_df = geocoder(location_input)
            intersected_df = intersection_check(input_df, df)

            m = leafmap.Map(center = [input_df['Latitude'][0], input_df['Longitude'][0]], zoom = 15, google_map = "HYBRID")
            style = {
                "stroke": True,
                "color": "#0000ff",
                "weight": 2,
                "opacity": 1,
                "fill": True,
                "fillColor": "#0000ff",
                "fillOpacity": 0.1,
            }
            m.add_points_from_xy(
                input_df,
                x="Longitude", 
                y="Latitude",
                icon_names=['gear', 'map', 'leaf', 'globe'],
            )
            m.add_gdf(intersected_df, layer_name="Region of Interest", style=style)
            m.to_streamlit(height=700)
            
            st.sidebar.expander("ℹ️ About", expanded = True)
        
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
            st.write("Based on the location of interest, we suggest the following skills:" + " " + skill_list)
            
            st.divider()
            
            st.subheader("💼 Job List:")
            st.write("Based on the skills, we suggest the following jobs:" + " " + job_list)
            st.caption(":blue[Hiring companies are listed in the table below.]")
            
            # job recommendation engine
            job_list = job_list.split(", ")
            result_df = []
            
            for i in range(0, len(job_list)):
                job_match = job_matcher(jobdata, column = 'title', string_to_match = str(job_list[i]))
                
                if job_match.empty:
                    continue
                else:
                    job_key = job_match['title'][0]
                    
                    result = job_recom_engine(jobdata, job_key = job_key)
                    result_df.append(result)
                
            result_df = pd.concat([df for df in result_df], ignore_index=True)
            st.table(result_df)