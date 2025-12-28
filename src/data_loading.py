"""
Data Acquisition & Caching Module
=================================
Description:
    Handles the retrieval of Skillcorner data (currently only physical aggregates are used).
    Utilizes Streamlit's @st.cache_data to optimize performance and 
    reduce redundant network requests.
"""

import json
import pandas as pd
import streamlit as st
import requests
from kloppy.skillcorner import load
import os

#{id}_dynamic_events.csv contains our Game Intelligence's dynamic events file (See further for specs.)
@st.cache_data
def load_dynamic_events(url):
    return pd.read_csv(url)

#{id}_match.json contains lineup information, time played, referee, pitch size...
@st.cache_data
def load_match_info(url):
    response = requests.get(url)
    data = json.loads(response.text)
    return pd.json_normalize(data)

#{id}_phases_of_play.csv contains our Game Intelligence's PHASES OF PLAY framework file. (See further for specs.)
@st.cache_data
def load_phases_of_play(url):
    return pd.read_csv(url)

#dataset on aggregated Physical data at the season level.
@st.cache_data
def load_aggregated_physical_data(url):
    return pd.read_csv(url)