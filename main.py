"""
SkillCorner Physical Scouting Tool - Streamlit Application
==========================================================
Author: Remi De Mesel
Date: 28/12/2025
Description: 
    A dashboard for analyzing physical metrics of Australian League players.
    Identifies archetypes via normalized data, percentile rankings, and 
    interactive radar comparisons.
"""

# =============================================================================
# 1. IMPORTS & CONFIGURATION
# =============================================================================

# Standard & Scientific Computing
import pandas as pd
import numpy as np

# GUI Framework
import streamlit as st

# Local Modules (Project Structure)
from src.data_loading import load_aggregated_physical_data
from src.UI_text_components import (
    title_with_icon,
    SCOUTING_TIPS,
    render_methodology_expander
)
from src.dashboard_logic import (
    prepare_physical_data_for_display,
    render_data_filters,
    plot_physical_radar
)

# Constants & Configuration
PAGE_CONFIG = {
    "page_title": "Analyst Web App",
    "page_icon": ":bar_chart:",
    "layout": "wide"
}

# Data Sources
# Note: Additional data sources (dynamic events, match info) can be added here.
URLS = {
    "physical_data": 'https://raw.githubusercontent.com/SkillCorner/opendata/refs/heads/master/data/aggregates/aus1league_physicalaggregates_20242025_midfielders.csv'
}


# =============================================================================
# 2. DATA MANAGEMENT
# =============================================================================

@st.cache_data
def load_all_data() -> dict:
    """
    Loads all required data sources.
    
    Returns:
        dict: A dictionary containing dataframes for each source.
    """
    data_store = {}
    
    try:
        data_store['aggregated_physical_data'] = load_aggregated_physical_data(URLS["physical_data"])
        # Future expansion: Load additional datasets here
    except Exception as e:
        st.error(f"Critical Error loading data: {e}")
        return {k: pd.DataFrame() for k in URLS.keys()}

    return data_store


# =============================================================================
# 3. UI COMPONENT FUNCTIONS
# =============================================================================

def render_sidebar_filters(df: pd.DataFrame) -> str:
    """
    Renders the sidebar position selector and displays dynamic scouting tips.
    
    Args:
        df (pd.DataFrame): The source dataframe containing position groups.
        
    Returns:
        str: The selected position group.
    """
    available_positions = sorted(df['position_group'].unique())
    
    # Selection Widget
    selected_position = st.sidebar.radio(
        '📌 Filter by Position Group', 
        options=available_positions
    )
    st.sidebar.divider()
    
    # Dynamic Advice Display
    tip_text = SCOUTING_TIPS.get(
        selected_position, 
        "Compare percentiles to identify physical outliers."
    )
    
    st.sidebar.info(f"💡 **Scout's Tip for {selected_position}:**\n\n{tip_text}")
    
    return selected_position

# =============================================================================
# 4. MAIN APPLICATION LOGIC
# =============================================================================

def main():
    # 1. Setup Page
    st.set_page_config(**PAGE_CONFIG)
    #add_custom_css()

    # 2. Load Data
    with st.spinner("Loading and processing data..."):
        data_store = load_all_data()

    if data_store['aggregated_physical_data'].empty:
        st.error("Aggregated physical data not loaded. Please check data source.")
        st.stop()

    # 3. Header & Methodology
    st.title("⚽ SkillCorner Physical Scouting Tool")
    render_methodology_expander()
    st.markdown("---")

    # 4. Sidebar Controls
    selected_position = render_sidebar_filters(data_store['aggregated_physical_data'])

    # 5. Process Data for Selected Position
    # Returns: Display DF (Raw), Percentile DF (Ranked), Radar Source DF
    df_display, df_percentile, df_radar_source, player_list = prepare_physical_data_for_display(
        data_store['aggregated_physical_data'], 
        selected_position
    )

    # 6. Filter Dashboard Section
    title_with_icon('📋', f"Filter Dashboard")
    
    # Render filters and get the final table
    # Logic for sliders/columns is handled inside 'render_data_filters'
    final_filtered_table = render_data_filters(df_display, df_percentile)
    
    # Display Table
    st.dataframe(final_filtered_table.dropna(axis=1, how='all').style.format(precision=2))
    st.divider()

    # 7. Radar Chart Section
    title_with_icon('📊', "Player Physical Profile Comparison (Radar Chart)")
    # Trigger Plot
    plot_physical_radar(df_radar_source, player_list)


if __name__ == "__main__":
    main()