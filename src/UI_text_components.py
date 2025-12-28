"""
UI Text Components & Methodology Module
=======================================
Description:
    Centralized repository for all educational content, scouting advice, 
    and methodology documentation. This ensures UI consistency across the app.
"""

import streamlit as st

def title_with_icon(icon: str, title: str):
    """Formats a header with an icon and aligned title."""
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

# =============================================================================
# 1. SCOUTING TIPS LOGIC
# =============================================================================
# Dynamic advice displayed in the sidebar based on the selected player position.

SCOUTING_TIPS = {
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

# =============================================================================
# 2. METHODOLOGY RENDERER
# =============================================================================

def render_methodology_expander():
    """
    Renders the educational 'Project Overview & Data Philosophy' section.
    Designed to provide transparency to the jury/users regarding data normalization
    and the proprietary 'Big Three' scoring logic.
    """
    with st.expander("ℹ️ Project Overview & Data Philosophy", expanded=False):
        # --- Section 1: Dashboard Goal ---
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

        # --- Section 2: Metric Table ---
        st.markdown("""
        | Metric | What it measures | Scouting Context |
        | :--- | :--- | :--- |
        | **Top Speed** | Peak sprint velocity 99th percentile (PSV99). | The top speed which the player is able to reach multiple times. |
        | **m/min (TIP)** | Distance covered when your team has the ball. | Work rate in possession and attacking support. |
        | **m/min (OTIP)** | Distance covered when the opponent has the ball. | Defensive work rate, tracking back, and pressing. |
        | **HSR (High Speed Running)** | Distance covered between 20 and 25 km/h. | Ability to repeatedly transition across the pitch at high speed. |
        | **Sprint Distance** | Distance covered above 25 km/h. | Ability to repeatedly transition across the pitch at sprint speed.|
        | **High Accel Count** | Number of rapid speed increases (>3 $m/s^2$). | Ability to initiate movements from a standing or jogging start. |
        | **Accel Time** | The average of the 3 best Time to HSR performances. | How quick a player can initiate a movement to high speed running. |
        | **High Decel Count** | Number of rapid speed decreases (<-3 $m/s^2$). | Ability to stop and change direction efficiently. |
        """)
        
        # --- Section 3: Scoring Logic ---
        st.markdown("""
            #### **The Big Three (Summary Scores)**
            Understand how the **Explosivity**, **Volume**, and **Total** scores are calculated. 
            These metrics are derived from the percentile rankings.
        """)

        col_ex, col_vol = st.columns(2)

        with col_ex:
            st.markdown("### ⚡ Explosivity")
            st.write("Measures high-end power and rapid movements.")
            st.table({
                "Component": ["Top Speed", "High Accels", "High Decels", "Sprint Count", "Sprint Distance"],
                "Weight": ["⭐⭐ (x2.0)", "⭐⭐ (x2.0)", "⭐ (x0.75)", "⭐ (x0.75)", "▫️ (x0.5)"]
            })
            with st.expander("View Explosivity Logic"):
                st.caption("Calculated by prioritizing peak velocity and the frequency of rapid accelerations over total sprinting distance.")

        with col_vol:
            st.markdown("### 🏃 Volume")
            st.write("Measures total work rate and aerobic engine.")
            st.table({
                "Component": ["Meters/Minute", "Running Dist", "HI Distance", "HI Count"],
                "Weight": ["⭐⭐ (x2.0)", "⭐ (x0.75)", "⭐ (x0.75)", "⭐ (x0.75)"]
            })
            with st.expander("View Volume Logic"):
                st.caption("Calculated by prioritizing your relative work rate (Meters/Min) to ensure session length doesn't bias the score.")

        # --- Section 4: Overall Benchmark ---
        st.subheader("🏆 Total Score")
        st.info("**Total = (Volume + Explosivity) / 2**")
        st.write("This is the overall performance rating, balancing engine (Volume) with power (Explosivity).")