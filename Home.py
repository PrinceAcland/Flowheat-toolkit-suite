"""
Home.py
--------
Landing page for the Fluid Flow & Heat Transfer Engineering Suite.

This is the entry point of the multi-page Streamlit application. Streamlit
automatically turns every file inside the pages/ folder into a separate page,
listed in the sidebar.

Run locally with:
    streamlit run Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Suite",
    page_icon="🛢️",
    layout="wide",
)

st.title("🛢️ Fluid Flow & Heat Transfer Engineering Suite")

st.markdown(
    """
    Welcome! This app is a small collection of petroleum-engineering
    calculators and a data dashboard, built for the **PE 262 Capstone
    Project** at KNUST.

    Use the sidebar on the left to open a module:
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔧 Pipe Flow Analyser")
    st.write(
        "Calculate velocity, Reynolds number, friction factor and "
        "pressure drop for flow through a pipe, and see how pressure "
        "drop changes with flow rate."
    )

with col2:
    st.subheader("🌡️ Heat Transfer Calculator")
    st.write(
        "Calculate steady-state conduction through a flat wall, and "
        "simulate how long it takes an object to cool using Newton's "
        "Law of Cooling."
    )

with col3:
    st.subheader("📊 Rock & Fluid Data Dashboard")
    st.write(
        "Upload a CSV of rock or fluid property data, filter it, and "
        "generate quick-look charts such as a porosity histogram and a "
        "porosity-permeability crossplot."
    )

st.divider()

st.markdown(
    """
    ### About this app
    All calculations are performed by a small object-oriented engineering
    library (`engineering.py`) containing the `Fluid`, `Pipe`, and
    `HeatExchanger` classes. The Streamlit pages only handle user input
    and display — every formula lives in that one module, so it can be
    tested and reused independently of the web interface.

    **Course:** PE 262 — Computer Programming for Petroleum Engineers,
    KNUST · **Project:** Capstone — Full Engineering Application
    """
)
