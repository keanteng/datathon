# load packages
import pandas as pd
import numpy as np
import streamlit as st
import geopandas as gpd
from backend.functions import *

# website settings
# turn off the side bar by default
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

## customize the side bar
st.sidebar.write("🤖 UN Datathon Solution Prototype")
st.sidebar.title("Resources:")
st.sidebar.info(
    """
    - GitHub repository: [Datathon](https://github.com/keanteng/datathon)
    """
)

st.sidebar.title("Team Member:")
st.sidebar.info(
    """
  Ang Zhi Nuo | Connie Hui Kang Yi | Khor Kean Teng | Ling Sing Cheng | Tan Yu Jing
    """
)

# Customize page title
st.title("🌍 Geo-based Employment Solution")

st.markdown("""
    We are a team from University Malaya, Malaysia. This is a demo of the solution prototype 🤖 for the UN Datathon 2023. 
""")

# user input 
location_input = st.text_input("Enter a location of interest:", "Kuala Lumpur Sentral")
submit = st.button("Compute", type = 'primary')

# setup the layout with columns
col1, col2 = st.columns(spec = [0.7, 0.3], gap = 'small')

# load data
df = gpd.read_file("data/shapefile/polbnda_mys.shp")

if submit:
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