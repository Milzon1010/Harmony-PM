import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import base64

# ---------------------- SETTING PAGE CONFIG ----------------------
st.set_page_config(page_title="Harmony PM Dashboard", layout="wide")

# ---------------------- CUSTOM BACKGROUND IMAGE ----------------------
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    css = f"""
        <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("tower_bg.png")

# ---------------------- CUSTOM SIDEBAR STYLE ----------------------
sidebar_css = """
<style>
    [data-testid="stSidebar"] > div:first-child {
        background-color: #8B0000;
        padding: 2rem 1rem;
        border-radius: 0px 20px 20px 0px;
    }

    .stButton > button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
</style>
"""
st.markdown(sidebar_css, unsafe_allow_html=True)

# ---------------------- TITLE ----------------------
st.markdown("<h1 style='color: white;'>📊 Harmony PM Dashboard</h1>", unsafe_allow_html=True)

# ---------------------- SIDEBAR SECTION ----------------------
st.sidebar.header("1. Upload & Pilih Kolom")
uploaded_file = st.sidebar.file_uploader("Upload Daily Update Excel (.xlsx)", type=["xlsx"])
if not uploaded_file:
    st.info("Silakan unggah file Excel standar update harian untuk menampilkan dashboard.")
    st.stop()

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data(file):
    return pd.read_excel(file, engine="openpyxl")

df = load_data(uploaded_file)

# ---------------------- SIDEBAR FILTER ----------------------
st.sidebar.header("2. Filter Data")
region_options = df["Region 6"].dropna().unique().tolist()
selected_regions = st.sidebar.multiselect("Pilih Region", options=region_options, default=region_options)

status_options = df["STATUS SITE"].dropna().unique().tolist()
selected_status = st.sidebar.multiselect("Pilih Status Site", options=status_options, default=status_options)

df_filtered = df[
    (df["Region 6"].isin(selected_regions)) &
    (df["STATUS SITE"].isin(selected_status))
]

# ---------------------- VISUALIZATION ----------------------
st.subheader("📍 Status Site Distribution by Region")
site_status_fig = px.histogram(
    df_filtered,
    x="Region 6",
    color="STATUS SITE",
    barmode="group",
    title="Distribusi Status Site per Region"
)
st.plotly_chart(site_status_fig, use_container_width=True)

st.subheader("📅 Timeline RFS Plan")
if "RFS Plan Date" in df_filtered.columns:
    df_filtered["RFS Plan Date"] = pd.to_datetime(df_filtered["RFS Plan Date"], errors="coerce")
    rfs_df = df_filtered.dropna(subset=["RFS Plan Date"])
    rfs_fig = px.histogram(
        rfs_df,
        x="RFS Plan Date",
        color="Region 6",
        nbins=30,
        title="Timeline RFS Plan"
    )
    st.plotly_chart(rfs_fig, use_container_width=True)

# ---------------------- SUMMARY ----------------------
st.subheader("📈 Summary Table")
summary = df_filtered.groupby(["Region 6", "STATUS SITE"]).size().unstack(fill_value=0)
st.dataframe(summary, use_container_width=True)

# ---------------------- EXPORT OPTION ----------------------
st.sidebar.header("3. Download Filtered Data")
buffer = BytesIO()
df_filtered.to_excel(buffer, index=False, engine='openpyxl')
st.sidebar.download_button(
    label="📥 Download Excel",
    data=buffer.getvalue(),
    file_name="filtered_harmony_pm_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
