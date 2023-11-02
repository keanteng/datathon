import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from geopy.geocoders import Nominatim
import leafmap.foliumap as leafmap
from shapely.geometry import Polygon, MultiPolygon

# convert to lat long
def geocoder(location_input):
    """
    Perform geocoding on location input. The input should be an address.

    Args:
        location_input (string): string input

    Returns:
        dataframe: a geodataframe with latitude and longitude and geometry
    """
    
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(location_input)
    
    location_df = pd.DataFrame({'City': location_input, 'Latitude': [location.latitude], 'Longitude': [location.longitude]})
    location_df  = gpd.GeoDataFrame(location_df, geometry=gpd.points_from_xy(location_df.Longitude, location_df.Latitude))
    return location_df

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
        if df['geometry'][index].contains(location_df['geometry'][0]) == True:
            df = df.loc[index,:].to_frame().transpose()
            df = df[['nam', 'laa', 'geometry']]
            df = gpd.GeoDataFrame(df, geometry=df.geometry, crs="EPSG:4326")
            df.reset_index()
            df['geometry'] = MultiPolygon([df['geometry'].to_numpy()[0]])
            return df

# for testing
#df = gpd.read_file("data/shapefile/polbnda_mys.shp")
#a = intersection_check(geocoder('Johor Bahru'), df)
#print(a)