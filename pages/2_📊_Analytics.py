import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Analytics – AgriAstra",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background:#0b1220; color:#f8fafc; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
h1,h2,h3,h4 { color:#ffffff; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/agriastra_final_dataset.csv")

df = load_data()

st.subheader("📊 Analytics Dashboard")

# ── Row 1 ──────────────────────────────────────────────────────────────────────
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("### 📈 NDVI Distribution")

    fig_ndvi = px.histogram(
        df,
        x="NDVI",
        nbins=30,
        color_discrete_sequence=["#00ff99"]
    )
    fig_ndvi.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220"
    )
    st.plotly_chart(fig_ndvi, use_container_width=True)

with row1_col2:
    st.markdown("### 🥧 Irrigation Recommendation Distribution")

    fig_irrigation = px.pie(
        df,
        names="Irrigation_Advisory",
        hole=0.55
    )
    fig_irrigation.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220"
    )
    st.plotly_chart(fig_irrigation, use_container_width=True)

# ── Row 2 ──────────────────────────────────────────────────────────────────────
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("### 📊 Rainfall Distribution")

    fig_rain = px.histogram(
        df,
        x="Rainfall",
        nbins=30,
        color_discrete_sequence=["#3399ff"]
    )
    fig_rain.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220"
    )
    st.plotly_chart(fig_rain, use_container_width=True)

with row2_col2:
    st.markdown("### 🌡️ NDVI by Moisture Stress")

    fig_stress = px.box(
        df,
        x="Moisture_Stress",
        y="NDVI",
        color="Moisture_Stress"
    )
    fig_stress.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220"
    )
    st.plotly_chart(fig_stress, use_container_width=True)

st.markdown("---")
st.markdown(
    "<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>",
    unsafe_allow_html=True
)
