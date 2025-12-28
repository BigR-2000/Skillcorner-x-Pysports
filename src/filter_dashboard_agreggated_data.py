import pandas as pd
import streamlit as st
from datetime import datetime
from scipy.stats import percentileofscore
from soccerplots.radar_chart import Radar


def calculate_age(geboortedatum):
    today = datetime.now()
    leeftijd = today.year - geboortedatum.year - ((today.month, today.day) < (geboortedatum.month, geboortedatum.day))
    return leeftijd

def calculate_percentile_score(B):
    percentiel_scores_dict = {}
    for kolomnaam in B.columns:
        percentiel_scores_dict[kolomnaam] = B[kolomnaam].apply(lambda x: percentileofscore(B[kolomnaam], x))
    return pd.DataFrame(percentiel_scores_dict)

def prepare_physical_data_for_display(df_phys: pd.DataFrame, position: str) -> pd.DataFrame:
    """
    Cleans, calculates per-minute metrics, and renames columns 
    for the Aggregated Physical Data display.
    """

    #Get the age instead of the birthdate, as this provides more valuable information to filter on
    physical_data_position = df_phys[df_phys['position_group'] == position].copy()
    physical_data_position['player_birthdate'] = pd.to_datetime(physical_data_position['player_birthdate'])
    physical_data_position['Age'] = physical_data_position['player_birthdate'].apply(calculate_age)
    physical_data_position.drop('player_birthdate', axis=1, inplace=True)
    
    # Calculate per-minute metrics (Tip: Team in Possession, Otip: Opposition in Possession)
    physical_data_position['hsr_metersperminute_tip'] = physical_data_position['hsr_distance_full_tip'] / physical_data_position['minutes_full_tip']
    physical_data_position['sprint_metersperminute_tip'] = physical_data_position['sprint_distance_full_tip'] / physical_data_position['minutes_full_tip']
    physical_data_position['hsr_metersperminute_otip'] = physical_data_position['hsr_distance_full_otip'] / physical_data_position['minutes_full_otip']
    physical_data_position['sprint_metersperminute_otip'] = physical_data_position['sprint_distance_full_otip'] / physical_data_position['minutes_full_otip']

    # Rename for clarity
    physical_data_position = physical_data_position.rename(columns={
        'player_short_name': 'Player',
        'team_name': 'Team',
        'psv99': 'Top Speed',
        'count_match': 'Matches',
        'timetohsr_top3': 'Top Accel Time',
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
    })

    # Create three versions: two for display (indexed) and one for radar processing (unindexed)
    df_for_display = physical_data_position.set_index(['Player', 'Age', 'Team', 'Matches'])
    df_for_display_percentile = calculate_percentile_score(df_for_display)
    df_for_radar = physical_data_position.drop(columns=['Age', 'Team', 'Matches'])
    
    #Now for the percentile dataframe we want to calculate some additional summarizing metrics; namely: 
    df_for_display_percentile['Explosivity'] = (((df_for_display_percentile['Top Speed'] * 2)+ (df_for_display_percentile['highaccel_count_full_all'] * 2) + (df_for_display_percentile['highdecel_count_full_all']*0.75) + (df_for_display_percentile['sprint_count_full_all'] * 0.75) + (df_for_display_percentile['sprint_distance_full_all'] * 0.5))/6)
    df_for_display_percentile['Volume'] = (((df_for_display_percentile['total_metersperminute_full_all'] * 2) + (df_for_display_percentile['running_distance_full_all']*0.75) + (df_for_display_percentile['hi_distance_full_all']*0.75) + (df_for_display_percentile['hi_count_full_all']*0.75))/4.5)
    df_for_display_percentile['Total'] = ((df_for_display_percentile['Volume']+ df_for_display_percentile['Explosivity'])/2)

    
    # Select final columns and set index for display
    display_cols = ['Top Speed', 'Top Accel Time', 
                    'Total m/min TIP', 'HSR m/min TIP', 'Sprint m/min TIP', 
                    'High Accel Count TIP', 'High Decel Count TIP', 
                    'Total m/min OTIP', 'HSR m/min OTIP', 'Sprint m/min OTIP',
                    'High Accel Count OTIP', 'High Decel Count OTIP']
    display_cols_percentile = display_cols + ['Explosivity', 'Volume', 'Total']
    display_cols_radar = ['Player'] + display_cols
                    
    df_for_display = df_for_display[display_cols]
    df_for_display_percentile = df_for_display_percentile[display_cols_percentile]
    df_for_radar = df_for_radar[display_cols_radar]

    return df_for_display, df_for_display_percentile,df_for_radar

def display_metric_definitions():

    st.markdown("""
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

# To use in your app:
# display_metric_definitions()


def plot_physical_radar(df, lijst):
        lijst2 = list(reversed(lijst))
        col1, col2, col3 = st.columns([1, 2, 1])
        try:
            with col1:
                options1 = st.radio('Speler1', options=lijst)
            with col3:
                options2 = st.radio('Speler2', options=lijst2)
        except:
            with col1:
                options1 = st.radio('speler1', options=lijst)
            with col3:
                options2 = st.radio('speler2', options=lijst2)

        test = df.loc[(df['Player'] == options1) | (df['Player'] == options2)]
        df1 = test.dropna(axis=1, how='any')

        numerieke_df = df.select_dtypes(include='number')
        gemiddelden = numerieke_df.mean()
        df_parameters = df.fillna(gemiddelden)
        
        df1.reset_index(drop=True, inplace= True)
        params = list(df1.columns)
        params = params[1:]
        params
        df2 = pd.DataFrame()
        df2 = df1.set_index('Player')
        with col2:
            st.dataframe(df2)
        
        ranges = []
        a_values = []
        b_values = []
        #st.markdown(df1[params])
        for x in params:
            if x == 'Top Speed':
                a = min(df_parameters[params][x])
                a = a * 0.96
            else:
                a = min(df_parameters[params][x])
                a = a * 0.96

            if x == 'Top Speed':
                b = max(df_parameters[params][x])
                b = b * 1.04
            else:
                b = max(df_parameters[params][x])
                b = b * 1.04
  
            ranges.append((a, b))
            a_values.append(a)
            b_values.append(b)

        #st.dataframe(a_values)
        player_1 = df1.iloc[0,0]
        player_2 = df1.iloc[1,0]

        for x in range(len(df1['Player'])):
            x = x - 1
            if df1.iloc[x, 0] == df1.iloc[0,0]:
                a_values = df1.iloc[x].values.tolist()
            if df1.iloc[x, 0] == df1.iloc[1,0]:
                b_values = df1.iloc[x].values.tolist()

        a_values = a_values[1:]
        b_values = b_values[1:]
        values = (a_values, b_values)

        title = dict(
        title_name=f'{player_1}',
        title_color='#B6282F',
        title_name_2=f'{player_2}',
        title_color_2='#344D94',
        title_fontsize=15,
        subtitle_fontsize=11
        )

        radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF",
              range_color="#FFFFFF")

        fig, ax = radar.plot_radar(ranges= ranges, params= params, values= values, 
                                radar_color=['red','blue'], 
                                title = title,
                                alphas = [0.3, 0.3],  
                                compare=True)
        fig.set_size_inches(12, 12)
        
        with col2:
            st.pyplot(fig)