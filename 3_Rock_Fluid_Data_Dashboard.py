"""
3_Rock_Fluid_Data_Dashboard.py
--------------------------------
Module C of the Capstone app: Rock & Fluid Data Dashboard.

Lets the user upload a CSV of rock/fluid property data (e.g. porosity,
permeability, water saturation from core analysis), view summary
statistics, filter the data interactively, view two charts (histogram and
crossplot), and download the filtered data as a new CSV.
"""

import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="📊", layout="wide")

st.title("📊 Module C — Rock & Fluid Data Dashboard")
st.caption(
    "Upload a CSV of rock/fluid property data (e.g. core-analysis "
    "porosity and permeability) to explore, filter, and export it."
)

with st.expander("ℹ️ Expected CSV format / don't have a file handy?"):
    st.markdown(
        """
        The dashboard works with **any** numeric CSV, but it is designed
        around typical core-analysis data with columns such as:

        `sample_id, porosity, permeability_md, water_saturation, depth_m`

        Don't have a file? Use the sample dataset below to try the
        dashboard, then upload your own real data.
        """
    )
    sample_csv_path = "sample_rock_fluid_data.csv"
    try:
        with open(sample_csv_path, "rb") as f:
            st.download_button(
                "⬇️ Download sample rock & fluid CSV",
                data=f,
                file_name="sample_rock_fluid_data.csv",
                mime="text/csv",
            )
    except FileNotFoundError:
        pass

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("👆 Upload a CSV file to get started.")
    st.stop()

# ----------------------------------------------------------------------
# Load and validate the data
# ----------------------------------------------------------------------
try:
    df = pd.read_csv(uploaded_file)
    if df.empty:
        st.error("The uploaded CSV file is empty.")
        st.stop()
except Exception as e:
    st.error(f"Could not read this file as a CSV: {e}")
    st.stop()

st.subheader("Raw data preview")
st.dataframe(df.head(20), use_container_width=True)
st.caption(f"{len(df):,} rows × {len(df.columns)} columns loaded.")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if not numeric_cols:
    st.warning(
        "No numeric columns were found in this file, so filtering and "
        "charting are not available. Please upload a CSV with at least "
        "one numeric column."
    )
    st.stop()

st.subheader("Summary statistics")
st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

# ----------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------
st.divider()
st.subheader("Filter the data")

filter_col = st.selectbox(
    "Column to filter on",
    options=numeric_cols,
    help="Choose a numeric column, then set a minimum value below to keep "
    "only rows at or above that value (e.g. porosity > 15%).",
)

col_min = float(df[filter_col].min())
col_max = float(df[filter_col].max())

threshold = st.slider(
    f"Show only rows where {filter_col} ≥ ...",
    min_value=col_min,
    max_value=col_max,
    value=col_min,
    help="Drag to set the minimum threshold for the selected column.",
)

filtered_df = df[df[filter_col] >= threshold].reset_index(drop=True)
st.write(f"**{len(filtered_df):,}** of **{len(df):,}** rows match this filter.")
st.dataframe(filtered_df, use_container_width=True)

# ----------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------
st.divider()
st.subheader("Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Histogram**")
    hist_col = st.selectbox("Column to histogram", options=numeric_cols, key="hist_col")
    fig1, ax1 = plt.subplots(figsize=(5.5, 4))
    ax1.hist(filtered_df[hist_col].dropna(), bins=20, color="#2ca02c", edgecolor="black", alpha=0.8)
    ax1.set_xlabel(hist_col)
    ax1.set_ylabel("Frequency")
    ax1.set_title(f"Distribution of {hist_col}")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with chart_col2:
    st.markdown("**Crossplot**")
    default_x = 0
    default_y = 1 if len(numeric_cols) > 1 else 0
    x_col = st.selectbox("X-axis column", options=numeric_cols, index=default_x, key="x_col")
    y_col = st.selectbox("Y-axis column", options=numeric_cols, index=default_y, key="y_col")
    fig2, ax2 = plt.subplots(figsize=(5.5, 4))
    ax2.scatter(filtered_df[x_col], filtered_df[y_col], color="#1f77b4", alpha=0.7, edgecolor="black")
    ax2.set_xlabel(x_col)
    ax2.set_ylabel(y_col)
    ax2.set_title(f"{y_col} vs {x_col}")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

# ----------------------------------------------------------------------
# Download filtered data
# ----------------------------------------------------------------------
st.divider()
st.subheader("Export filtered data")

csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)

st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=csv_buffer.getvalue(),
    file_name="filtered_rock_fluid_data.csv",
    mime="text/csv",
)
