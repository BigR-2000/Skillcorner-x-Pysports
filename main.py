# =============================================================================
# 1. IMPORTS
# =============================================================================

# Data Handling & Scientific Computing
import pandas as pd
import numpy as np

import streamlit as st

from src.data_loading import load_aggregated_physical_data
from src.filter_dashboard_agreggated_data import (
    prepare_physical_data_for_display,
    plot_physical_radar,
    display_metric_definitions
)
from src.app_styling import add_custom_css

st.set_page_config(layout="wide")

st.markdown("""

<style> /* */ html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp { background-color: #0e1117 !important; color: #fafafa !important; }

</style>

""", unsafe_allow_html=True)

URLS = {
    #"dynamic_events": "https://raw.githubusercontent.com/SkillCorner/opendata/master/data/matches/1886347/1886347_dynamic_events.csv",
    #"match_info": "https://raw.githubusercontent.com/SkillCorner/opendata/refs/heads/master/data/matches/1886347/1886347_match.json",
    #"phases_of_play": 'https://raw.githubusercontent.com/SkillCorner/opendata/refs/heads/master/data/matches/1886347/1886347_phases_of_play.csv',
    "physical_data": 'https://raw.githubusercontent.com/SkillCorner/opendata/refs/heads/master/data/aggregates/aus1league_physicalaggregates_20242025_midfielders.csv'
}

def title_with_icon(icon: str, title: str):
    """Formats a header with an icon using custom CSS."""
    st.markdown(
        f"<div class='title-wrapper'><div class='icon'>{icon}</div><h3>{title}</h3></div>", 
        unsafe_allow_html=True
    )

def title_with_icon(icon: str, title: str):
    """Formats a header with a larger icon and aligned title."""
    st.markdown(
        f"""
        <style>
            .title-wrapper {{
                display: flex;
                align-items: center;
                gap: 1Opx; /* Space between icon and text */
                margin-bottom: 10px;
            }}
            .icon {{
                font-size: 1.75rem; /* Adjust this to make the icon bigger */
                line-height: 1;
            }}
            .title-wrapper h3 {{
                margin: 0; /* Remove default margin for perfect alignment */
                font-size: 1.75rem;
            }}
        </style>
        <div class='title-wrapper'>
            <div class='icon'>{icon}</div>
            <h3>{title}</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )

@st.cache_data
def load_all_data():
    """Loads all data sources and returns them as a dictionary."""
    data = {}
    
    # Load data using external functions
    try:
        #data['dynamic_events'] = load_dynamic_events(URLS["dynamic_events"])
        #data['match_info'] = load_match_info(URLS["match_info"])
        # NOTE: Using load_tracking_data2 for the specified local path
        #data['phases_of_play'] = load_phases_of_play(URLS["phases_of_play"])
        data['aggregated_physical_data'] = load_aggregated_physical_data(URLS["physical_data"])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return empty dataframes/dicts in case of load failure
        return {k: pd.DataFrame() for k in URLS.keys()}

    return data

# =============================================================================
# 4. STREAMLIT APPLICATION LOGIC
# =============================================================================

# --- Page Configuration and Styling ---
st.set_page_config(
    page_title='Analyst Web App',
    page_icon=':bar_chart:',
    layout="wide"
)
add_custom_css() # Apply custom styling from local module

# --- Data Loading ---
with st.spinner("Loading and processing data..."):
    data = load_all_data()


# --- Application Header and Introduction ---
st.title("⚽ SkillCorner Physical Scouting Tool")
# --- Expander for Methodology ---
with st.expander("ℹ️ Project Overview & Data Philosophy", expanded=False):
    st.markdown("""
    ### 🎯 Dashboard Goal
    The **SkillCorner Physical Scouting Tool** is designed to identify athletic archetypes within the **Australian League 24/25**. 
    By analyzing aggregated physical data, this tool helps recruitment departments move beyond "total distance" to find players who possess the specific **explosivity** or **sustained intensity** required for their tactical system.

    ### 🔬 Data Philosophy
    Raw physical totals can be misleading (e.g., a player might have high distance simply because they played more minutes). This dashboard solves that by using:
    
    * **Normalized Intensity:** All distance metrics are calculated as **Meters per Minute**, providing a fair comparison across the squad regardless of minutes played.
    * **Contextual Breakdown:** We distinguish between **TIP** (Team In Possession) and **OTIP** (Opposition In Possession). This reveals if a player’s physical output is driven by attacking transitions or defensive pressing.
    * **Percentile Benchmarking:** Every player is ranked against their specific **Position Group**, ensuring a Center Back is compared to other Center Backs, not to Wingers.
    
    ---
    
    ### 📖 The Scouting Metrics Explained
                
    #### **Physical Component Definitions**
    """)

    # Using a Markdown table for the definitions
    st.markdown("""
    | Metric | What it measures | Scouting Context |
    | :--- | :--- | :--- |
    | **Top Speed** | Peak sprint velocity 99th percentile (PSV99).  | The top speed which the player is able to reach multiple times. |
    | **Top Accel Time** | Efficiency in reaching high speeds. | "Quickness" and reactivity in tight spaces. |
    | **High Accel Count** | Number of rapid speed increases (>3 $m/s^2$). | Ability to initiate movements from a standing or jogging start. |
    | **High Decel Count** | Number of rapid speed decreases (<-3 $m/s^2$). | Ability to stop and change direction efficiently. |
    | **m/min (TIP)** | Distance covered when your team has the ball. | Work rate in possession and attacking support. |
    | **m/min (OTIP)** | Distance covered when the opponent has the ball. | Defensive work rate, tracking back, and pressing. |
    | **HSR (High Speed Running)** | Distance covered between 20 and 25 km/h. | Ability to repeatedly transition across the pitch at high speed. |
    | **Sprint Distance** | Distance covered above 25 km/h. | Ability to repeatedly transition across the pitch at sprint speed.|  
    """)
    
    

    st.markdown("""
        #### **The Big Three (Summary Scores)**
        Understand how the **Explosivity**, **Volume**, and **Total** scores are calculated. 
        These metrics are derived from the percentile rankings.
    """)

    # --- EXPLOSIVITY & VOLUME COLUMNS ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚡ Explosivity")
        st.write("Measures high-end power and rapid movements.")
        
        # Displaying weights as a simple list or table
        st.table({
            "Component": ["Top Speed", "High Accels", "High Decels", "Sprint Count", "Sprint Distance"],
            "Weight": ["⭐⭐ (x2.0)", "⭐⭐ (x2.0)", "⭐ (x0.75)", "⭐ (x0.75)", "▫️ (x0.5)"]
        })
        
        with st.expander("View Explosivity Logic"):
            st.caption("Calculated by prioritizing peak velocity and the frequency of rapid accelerations over total sprinting distance.")

    with col2:
        st.markdown("### 🏃 Volume")
        st.write("Measures total work rate and aerobic engine.")
        
        st.table({
            "Component": ["Meters/Minute", "Running Dist", "HI Distance", "HI Count"],
            "Weight": ["⭐⭐ (x2.0)", "⭐ (x0.75)", "⭐ (x0.75)", "⭐ (x0.75)"]
        })
        
        with st.expander("View Volume Logic"):
            st.caption("Calculated by prioritizing your relative work rate (Meters/Min) to ensure session length doesn't bias the score.")

        # --- TOTAL SCORE ---
    st.subheader("🏆 Total Score")
    st.info("**Total = (Volume + Explosivity) / 2**")
    st.write("This is the overall performance rating, balancing engine (Volume) with power (Explosivity).")

st.markdown("---")
# =========================================================================
# 5. ANALYSIS SECTIONS
# =========================================================================
if data['aggregated_physical_data'].empty:
    st.error("Aggregated physical data not loaded.")


available_positions = data['aggregated_physical_data']['position_group'].unique()
position_analysis = st.sidebar.radio('📌 Filter by Position Group', options=available_positions)
st.sidebar.divider()
tips = {
    "Center Forward": (
        "* **Space Threat:** Use **Top Speed** to see their physical capacity to exploit the space behind a defensive line.\n"
        "* **Pressing Intensity:** Use **OTIP HSR** to identify players who maintain high-intensity work rates when out of possession."
    ),
    "Central Defender": (
        "* **Agility/Reactivity:** Use **High Decel Count** to see how quickly they can brake and adjust their body to opponent movement.\n"
        "* **Recovery Pace:** Use **Top Speed** to identify defenders capable of chasing down attackers in transition."
    ),
    "Midfield": (
        "* **Active Engine:** Use **Total m/min** to find players who are constantly mobile.\n"
        "* **Workload Capacity:** Use **Volume Score** to identify players capable of sustaining high intensity meters for the full 90 minutes."
    ),
    "Wide Attacker": (
        "* **1v1 Impact:** Use **Explosivity** to find players with strong acceleration and speed needed to beat defenders.\n"
        "* **Attacking Threat:** Use **TIP Sprinting** to measure how much they use their top gear during possession, e.g. to drive transition play and execute vertical runs behind the defense."
    ),
    "Full Back": (
        "* **Repeated Efforts:** Use **HSR Distance** to measure the stamina required for consistent overlapping runs.\n"
        "* **Two-Way Work:** Use **TIP vs OTIP HSR m/min** to ensure they balance attacking support with defensive recovery."
    )
}

# Display using a compact info box
current_tip = tips.get(position_analysis, "Compare percentiles to identify physical outliers.")
st.sidebar.info(f"💡 **Scout's Tip for {position_analysis}:**\n\n{current_tip}")

# --- Overview Table ---
title_with_icon('📋', f"Filter Dashboard")


physical_data_display, physical_data_percentile, physical_data_radar_source = prepare_physical_data_for_display(
    data['aggregated_physical_data'], 
    position_analysis
)

st.checkbox('Show Percentile Scores', key='percentile_toggle')
if st.session_state['percentile_toggle']:
    A = physical_data_percentile.reset_index()
else:
    A = physical_data_display.reset_index()

col1, col2, col3, col4, col5 = st.columns([3, 0.75, 3, 0.75, 2])
with col1:
    min_age = int(A['Age'].min())
    max_age = int(A['Age'].max())
    leeftijd = st.slider('Age', min_value=min_age, max_value=max_age, value=(17, 42))
    A = A[(A['Age'] >= leeftijd[0]) & (A['Age'] <= leeftijd[1])]
    min_matches = int(A['Matches'].min())
    max_matches = int(A['Matches'].max())
    matchen = st.slider('Matches', min_value=min_matches, max_value=max_matches, value=(min_matches, max_matches))
    A = A[(A['Matches'] >= matchen[0]) & (A['Matches'] <= matchen[1])]
    A = A.set_index(['Player', 'Team', 'Age', 'Matches'])
with col3:
    metrics = st.multiselect('show parameters', ['Top Speed', 'Top Accel Time', 
        'Total m/min TIP', 'HSR m/min TIP', 'Sprint m/min TIP', 
        'High Accel Count TIP', 'High Decel Count TIP', 
        'Total m/min OTIP', 'HSR m/min OTIP', 'Sprint m/min OTIP',
        'High Accel Count OTIP', 'High Decel Count OTIP'])
    if not metrics:
        metrics =  ['Top Speed', 'Top Accel Time', 
        'Total m/min TIP', 'HSR m/min TIP', 'Sprint m/min TIP', 
        'High Accel Count TIP', 'High Decel Count TIP', 
        'Total m/min OTIP', 'HSR m/min OTIP', 'Sprint m/min OTIP',
        'High Accel Count OTIP', 'High Decel Count OTIP']
    if st.session_state['percentile_toggle']:
        metrics = ['Explosivity', 'Volume', 'Total'] + metrics 
    A = A[metrics]
with col5:
    filter = st.multiselect('filter parameters', metrics)
    if filter:
        for parameter in filter:
            min_val = int(A[parameter].min())
            max_val = int(A[parameter].max())
            parafilter = st.slider(parameter, min_value=min_val, max_value=max_val, value=(min_val, max_val))
            A = A[(A[parameter] >= parafilter[0]) & (A[parameter] <= parafilter[1])]
st.dataframe(A.style.format(precision=2)) # Format numbers for clarity
st.divider()

# --- Radar Chart Comparison ---
title_with_icon('📊', "Player Physical Profile Comparison (Radar Chart)")

average_player = physical_data_radar_source.copy()
average_player['Player'] = f'Average {position_analysis}'
average_player_mean = average_player.groupby('Player').mean().reset_index()


player_list = sorted(physical_data_radar_source['Player'].tolist())
physical_data_radar_source = pd.concat([physical_data_radar_source, average_player_mean], ignore_index=True)
player_list.append(f'Average {position_analysis}')

plot_physical_radar(physical_data_radar_source, player_list)
    
