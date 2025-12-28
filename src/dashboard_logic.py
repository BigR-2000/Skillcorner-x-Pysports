import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from scipy.stats import percentileofscore
from soccerplots.radar_chart import Radar


# =============================================================================
# 1. GLOBAL CONFIGURATIONS
# =============================================================================

DEFAULT_METRICS = [
    'Top Speed', 'Accel Time', 
    'Total m/min TIP', 'HSR m/min TIP', 'Sprint m/min TIP', 
    'High Accel Count TIP', 'High Decel Count TIP', 
    'Total m/min OTIP', 'HSR m/min OTIP', 'Sprint m/min OTIP',
    'High Accel Count OTIP', 'High Decel Count OTIP'
]

COLUMN_MAPPING = {
    'player_short_name': 'Player',
    'team_name': 'Team',
    'psv99': 'Top Speed',
    'count_match': 'Matches',
    'timetohsr_top3': 'Accel Time',
    'total_metersperminute_full_tip': 'Total m/min TIP',
    'hsr_metersperminute_tip': 'HSR m/min TIP',
    'sprint_metersperminute_tip': 'Sprint m/min TIP',
    'highaccel_count_full_tip': 'High Accel Count TIP',
    'highdecel_count_full_tip': 'High Decel Count TIP',
    'total_metersperminute_full_otip': 'Total m/min OTIP',
    'hsr_metersperminute_otip': 'HSR m/min OTIP',
    'sprint_metersperminute_otip': 'Sprint m/min OTIP',
    'highaccel_count_full_otip': 'High Accel Count OTIP',
    'highdecel_count_full_otip': 'High Decel Count OTIP'
}

# =============================================================================
# 2. INTERNAL UTILITIES
# =============================================================================

def calculate_age(birthdate):
    """Calculates player age from birthdate string/object."""
    today = datetime.now()
    leeftijd = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return leeftijd

def calculate_percentile_score(df_input):
    """Computes column-wise percentile rankings (0-100) for all numeric fields."""
    percentiel_scores_dict = {}
    for column in df_input.columns:
        percentiel_scores_dict[column] = df_input[column].apply(
            lambda x: percentileofscore(df_input[column], x)
        )
    return pd.DataFrame(percentiel_scores_dict)

# =============================================================================
# 3. DATA TRANSFORMATION PIPELINE
# =============================================================================

def prepare_physical_data_for_display(df_phys: pd.DataFrame, position: str):
    """
    Main pipeline: 
    1. Filters by position 
    2. Normalizes physical metrics to per-minute values 
    3. Generates the 'Big Three' composite scores.
    4. Prepares the benchmark 'Average Player' for Radar comparison.
    """

    # --- Step 1: Age & Position Filtering ---
    physical_data_position = df_phys[df_phys['position_group'] == position].copy()
    physical_data_position['player_birthdate'] = pd.to_datetime(physical_data_position['player_birthdate'])
    physical_data_position['Age'] = physical_data_position['player_birthdate'].apply(calculate_age)
    physical_data_position.drop('player_birthdate', axis=1, inplace=True)
    
    # --- Step 2: Physical Normalization ---
    physical_data_position['hsr_metersperminute_tip'] = physical_data_position['hsr_distance_full_tip'] / physical_data_position['minutes_full_tip']
    physical_data_position['sprint_metersperminute_tip'] = physical_data_position['sprint_distance_full_tip'] / physical_data_position['minutes_full_tip']
    physical_data_position['hsr_metersperminute_otip'] = physical_data_position['hsr_distance_full_otip'] / physical_data_position['minutes_full_otip']
    physical_data_position['sprint_metersperminute_otip'] = physical_data_position['sprint_distance_full_otip'] / physical_data_position['minutes_full_otip']

    # --- Step 3: Professional Renaming ---
    physical_data_position = physical_data_position.rename(columns=COLUMN_MAPPING)

    # --- Step 4: Percentile & Logic Calculation ---
    df_for_display = physical_data_position.set_index(['Player', 'Age', 'Team', 'Matches'])
    df_for_display_percentile = calculate_percentile_score(df_for_display)
    
    # Your specific weighting logic
    df_for_display_percentile['Explosivity'] = (
        ((df_for_display_percentile['Top Speed'] * 2) + 
         (df_for_display_percentile['highaccel_count_full_all'] * 2) + 
         (df_for_display_percentile['highdecel_count_full_all'] * 0.75) + 
         (df_for_display_percentile['sprint_count_full_all'] * 0.75) + 
         (df_for_display_percentile['sprint_distance_full_all'] * 0.5)) / 6
    )
    
    df_for_display_percentile['Volume'] = (
        ((df_for_display_percentile['total_metersperminute_full_all'] * 2) + 
         (df_for_display_percentile['running_distance_full_all'] * 0.75) + 
         (df_for_display_percentile['hi_distance_full_all'] * 0.75) + 
         (df_for_display_percentile['hi_count_full_all'] * 0.75)) / 4.5
    )
    
    df_for_display_percentile['Total'] = ((df_for_display_percentile['Volume'] + df_for_display_percentile['Explosivity']) / 2)

    # --- Step 5: Column Selection for Displays ---
    display_cols = DEFAULT_METRICS
    display_cols_percentile = display_cols + ['Explosivity', 'Volume', 'Total']
    display_cols_radar = ['Player'] + display_cols
    
    df_display_final = df_for_display[display_cols]
    df_percentile_final = df_for_display_percentile[display_cols_percentile]

    # --- Step 6: Radar Data & Benchmark Calculation ---
    # Create the base radar dataframe
    df_for_radar = physical_data_position[display_cols_radar].copy()

    # Create Synthetic Average Player for Benchmark
    average_player_df = df_for_radar.copy()
    average_player_df['Player'] = f'Average {position}'
    
    # Calculate means only for numeric columns
    numeric_cols = average_player_df.select_dtypes(include=[np.number]).columns
    average_player_mean = average_player_df.groupby('Player')[numeric_cols].mean().reset_index()

    # Prepare player list for the Streamlit radio/dropdown
    player_list = sorted(df_for_radar['Player'].unique().tolist())
    player_list.append(f'Average {position}')

    # Combine data for final plotting source
    final_radar_data = pd.concat([df_for_radar, average_player_mean], ignore_index=True)

    return df_display_final, df_percentile_final, final_radar_data, player_list

# =============================================================================
# 4. INTERACTIVE UI FILTERS
# =============================================================================

def render_data_filters(df_display: pd.DataFrame, df_percentile: pd.DataFrame):
    """
    Handles the complex filtering logic (Age, Matches, Metrics, Sliders).
    Returns the fully filtered DataFrame ready for display.
    """
    
    # Toggle Logic: Choose between Raw Data or Percentile Data
    st.checkbox('Show Percentile Scores', key='percentile_toggle')
    
    if st.session_state['percentile_toggle']:
        working_df = df_percentile.reset_index()
    else:
        working_df = df_display.reset_index()

    # Layout: 5 Columns for responsive filtering UI
    c1, _, c2, _, c3 = st.columns([3, 0.75, 3, 0.75, 2])

    # Column 1: Demographic Sliders
    with c1:
        # Age Filter
        min_age, max_age = int(working_df['Age'].min()), int(working_df['Age'].max())
        age_range = st.slider('Age', min_value=min_age, max_value=max_age, value=(17, 42))
        working_df = working_df[(working_df['Age'] >= age_range[0]) & (working_df['Age'] <= age_range[1])]

        # Matches Filter
        min_match, max_match = int(working_df['Matches'].min()), int(working_df['Matches'].max())
        match_range = st.slider('Matches', min_value=min_match, max_value=max_match, value=(min_match, max_match))
        working_df = working_df[(working_df['Matches'] >= match_range[0]) & (working_df['Matches'] <= match_range[1])]

        # Reset Index for Display
        working_df = working_df.set_index(['Player', 'Team', 'Age', 'Matches'])

    # Column 2: Metric Column Selection
    with c2:
        selected_columns = st.multiselect('Show parameters', DEFAULT_METRICS)
        
        # Fallback if empty
        if not selected_columns:
            selected_columns = DEFAULT_METRICS
            
        # Add summary scores if in Percentile mode
        if st.session_state['percentile_toggle']:
            selected_columns = ['Explosivity', 'Volume', 'Total'] + selected_columns 
            
        working_df = working_df[selected_columns]

    # Column 3: Value-based Filtering (Dynamic Sliders)
    with c3:
        params_to_filter = st.multiselect('Filter parameters', selected_columns)
        if params_to_filter:
            for param in params_to_filter:
                p_min, p_max = int(working_df[param].min()), int(working_df[param].max())
                val_range = st.slider(param, min_value=p_min, max_value=p_max, value=(p_min, p_max))
                working_df = working_df[(working_df[param] >= val_range[0]) & (working_df[param] <= val_range[1])]

    return working_df


def plot_physical_radar(df_radar_source: pd.DataFrame, player_list: list):
    """
    Renders an interactive comparison radar chart between two selected players.
    Includes automated scaling and metric inversion for time-based parameters.
    """
    # 1. Selection UI Setup
    # Reverse the list for the second selector so both players aren't the same by default
    player_list_reversed = list(reversed(player_list))
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    # Selection widgets with safety handling for labels
    try:
        with col_left:
            player1_select = st.radio('Select Player 1', options=player_list)
        with col_right:
            player2_select = st.radio('Select Player 2', options=player_list_reversed)
    except:
        with col_left:
            player1_select = st.radio('player 1', options=player_list)
        with col_right:
            player2_select = st.radio('player 2', options=player_list_reversed)

    # 2. Data Preparation for Selected Players
    # Filter the source data for the two chosen entities (Player or Average)
    selected_players_df = df_radar_source.loc[
        (df_radar_source['Player'] == player1_select) | (df_radar_source['Player'] == player2_select)
    ]
    
    # Remove any columns with missing data to ensure a clean radar plot
    df_filtered = selected_players_df.dropna(axis=1, how='any')

    # Calculate global averages for data imputation/filling
    numeric_only = df_radar_source.select_dtypes(include='number')
    global_means = numeric_only.mean()
    df_with_imputed_values = df_radar_source.fillna(global_means)
    
    # 3. Parameter and Display Setup
    df_filtered.reset_index(drop=True, inplace=True)
    metric_params = list(df_filtered.columns)[1:] # Exclude 'Player' column
    
    # Display the raw data table for quick numerical comparison
    comparison_table = df_filtered.set_index('Player')
    with col_center:
        st.dataframe(comparison_table)
    
    # 4. Range and Metric Logic (Normalization)
    # Soccerplots requires specific ranges for each axis.
    # Note: 'Accel Time' is inverted because a lower time is a better physical performance.
    radar_ranges = []
    player1_values = []
    player2_values = []

    for metric in metric_params:
        # Determine the "Floor" (a) and "Ceiling" (b) for the radar axes
        if metric == 'Accel Time':
            # Invert: Max value becomes the center of the radar
            axis_min = max(df_with_imputed_values[metric_params][metric]) * 1.04
            axis_max = min(df_with_imputed_values[metric_params][metric]) * 0.96
        else:
            # Standard: Min value is the center, Max is the edge
            axis_min = min(df_with_imputed_values[metric_params][metric]) * 0.96
            axis_max = max(df_with_imputed_values[metric_params][metric]) * 1.04
  
        radar_ranges.append((axis_min, axis_max))

    # 5. Value Extraction for Plotting
    # Identify which row belongs to which player selection
    name_p1 = df_filtered.iloc[0, 0]
    name_p2 = df_filtered.iloc[1, 0]

    for i in range(len(df_filtered['Player'])):
        # Adjusted loop to map values correctly to player names
        idx = i - 1
        if df_filtered.iloc[idx, 0] == name_p1:
            player1_values = df_filtered.iloc[idx].values.tolist()[1:]
        if df_filtered.iloc[idx, 0] == name_p2:
            player2_values = df_filtered.iloc[idx].values.tolist()[1:]

    radar_values = (player1_values, player2_values)

    # 6. Visualization Configuration
    chart_title = dict(
        title_name=f'{name_p1}',
        title_color='#B6282F',     
        title_name_2=f'{name_p2}',
        title_color_2='#344D94',    
        title_fontsize=15,
        subtitle_fontsize=11
    )

    # Initialize the Radar object with a dark-mode scouting aesthetic
    radar_viz = Radar(
        background_color="#121212", 
        patch_color="#28252C", 
        label_color="#FFFFFF",
        range_color="#FFFFFF"
    )
    # Initialize the Radar object with a dark-mode scouting aesthetic
    radar_viz = Radar(
        background_color="#FFFFFF", 
        patch_color="#D7D5DA", 
        label_color="#121212",
        range_color="#121212"
    )

    # Plotting the figure
    fig, ax = radar_viz.plot_radar(
        ranges=radar_ranges, 
        params=metric_params, 
        values=radar_values, 
        radar_color=['red', 'blue'], 
        title=chart_title,
        alphas=[0.3, 0.3],  
        compare=True
    )
    fig.set_size_inches(12, 12)
    
    # 7. Rendering and Footnotes
    with col_center:
        st.pyplot(fig)
        st.divider()
        st.subheader("Possible Extensions")
        st.write("Future enhancements could include the integration of the SkillCorner Dynamic Events dataset, aggregated over multiple games.")
        st.write("Incorporating this data would shift the analysis beyond raw physical metrics to evaluate on-field efficiency.")
        st.write("For example, analyzing off-the-ball intelligence, such as the frequency of 'dangerous runs', and defensive contributions like counter-pressing success rates, or adding technical layers such as line-breaking passes and passing accuracy under pressure.")
        st.write("Integrating these physical, tactical, and technical scales would offer a significantly deeper understanding of a player's overall impact, all based on the available Skillcorner data.")