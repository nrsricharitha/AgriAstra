import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dataset – AgriAstra",
    page_icon="📋",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background:#0b1220; color:#f8fafc; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
h1,h2,h3,h4 { color:#ffffff; }
[data-testid="stDataFrame"] { border-radius:12px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/agriastra_final_dataset.csv")

df = load_data()

st.subheader("📋 Dataset Preview")

# ── Search / filter ────────────────────────────────────────────────────────────
search = st.text_input("🔍 Filter by Moisture Stress", placeholder="e.g. High, Moderate, Low")

if search:
    filtered = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
else:
    filtered = df

st.markdown(f"Showing **{len(filtered)}** of **{len(df)}** records")

st.dataframe(filtered.head(20), use_container_width=True)

st.markdown("---")

# ── Basic stats ────────────────────────────────────────────────────────────────
with st.expander("📊 Descriptive Statistics"):
    st.dataframe(df.describe(), use_container_width=True)

st.markdown("---")
st.markdown(
    "<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>",
    unsafe_allow_html=True
)
