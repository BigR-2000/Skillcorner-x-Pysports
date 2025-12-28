import json
import pandas as pd
import streamlit as st
import requests
from kloppy.skillcorner import load
import os


# ---Functions to open the data files---
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

#{id}_tracking_extrapolated.jsonl contains the tracking data (the players and the ball).
@st.cache_data
def load_tracking_data2(file_path):
    # JSONL = one JSON object per line
    with open(file_path, 'r') as f:
        data = [json.loads(line) for line in f]  # list of dictionaries, one per frame
    # Now let's extract the tracking data per player per frame in a df, out of the list of dictionaries..
    all_players = [] 
    for frame in data:
        players = frame['player_data']
        for player in players:
            # add frame info to each player
            player['frame'] = frame['frame']
            player['timestamp'] = frame['timestamp']
            player['period'] = frame['period']
            player['possession'] = frame['possession']
            player['ball_data'] = frame['ball_data']
            all_players.append(player)
        frame['ball_data']['frame'] = frame['frame']
        frame['ball_data']['timestamp'] = frame['timestamp']
    all_players.append(frame['ball_data'])
    # Convert to DataFrame
    return pd.json_normalize(all_players)

#{id}_tracking_extrapolated.jsonl contains the tracking data (the players and the ball).
@st.cache_data
def load_tracking_data(tracking_file_jsonl, match_file):
    # --- Step 1: convert JSONL to JSON ---
    tracking_file_json = r"C:\Users\remid\OneDrive\Documenten\Skillcorner-Pysports_project\tracking_data\1886347_tracking_extrapolated.json"

    # Check of JSON file already exists
    if os.path.exists(tracking_file_json):
        print("tracking data already converted to JSON")
    else:
        # Only convert if it has not been done already
        data = []
        with open(tracking_file_jsonl, 'r') as f:
            for line in f:
                data.append(json.loads(line))

        with open(tracking_file_json, 'w') as f:
            json.dump(data, f)

        print("✅ JSONL geconverteerd naar JSON")

    tracking_data = load(
        meta_data=match_file,
        raw_data=tracking_file_json,
    )
    df_tracking = tracking_data.to_pandas()
    return df_tracking

#{id}_phases_of_play.csv contains our Game Intelligence's PHASES OF PLAY framework file. (See further for specs.)
@st.cache_data
def load_phases_of_play(url):
    return pd.read_csv(url)

#dataset on aggregated Physical data at the season level.
@st.cache_data
def load_aggregated_physical_data(url):
    return pd.read_csv(url)