import streamlit as st

#Function with CSS for titles and containers
def add_custom_css():
    """Voegt algemene CSS-styling toe voor titels en containers."""
    st.markdown("""
        <style>
            .title-wrapper {
                display: flex;
                align-items: center;
            }
            .icon {
                margin-right: 10px;
            }
            /* Styling voor de Match Header Container */
            .match-header {
                padding: 10px 15px;
                border-radius: 12px;
                background-color: #44445E; /* grey */
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                width: 100%;
                margin-left: auto;
                margin-right: auto;
            }
            .match-title {
                font-size: 40px;
                font-weight: 800;
                color: white;
            }
            .match-score {
                font-size: 55px;
                font-weight: 900;
                color: white;
                margin-top: -10px;
            }
            .match-meta {
                font-size: 20px;
                color: #dddddd;
                margin-top: -5px;
            }
        </style>
    """, unsafe_allow_html=True)

def title_with_icon(icon, title):
    """Show title with icon."""
    st.markdown(f"<div class='title-wrapper'><div class='icon'>{icon}</div><h4>{title}</h4></div>", unsafe_allow_html=True)