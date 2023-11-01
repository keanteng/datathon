# load packages
import pandas as pd
import numpy as np
import streamlit as st


# website settings
st.set_page_config(layout="wide")

## customize the side bar
st.sidebar.title("Resources:")
st.sidebar.info(
    """
    - GitHub repository: [Datathon](https://github.com/keanteng/datathon)
    """
)

st.sidebar.title("Created By:")
st.sidebar.info(
    """
  Team: xxx
    """
)

# Customize page title
st.title("🌍 Geo-based Employment Solution")

st.markdown("""
    This is a demo of the solution prototype for the Datathon 2023.
""")