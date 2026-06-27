import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Model – AgriAstra",
    page_icon="🤖",
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

st.markdown("## 🤖 AI Model Performance")

left, right = st.columns([1, 2])

# ── Summary Card ───────────────────────────────────────────────────────────────
with left:
    st.markdown("""
    <div style="
    background:#16213E;
    padding:18px;
    border-radius:15px;
    border-left:5px solid #22c55e;
    box-shadow:0 4px 10px rgba(0,0,0,.35);
    ">

    <h3 style="color:white;margin-top:0;">
    🤖 AI Model Summary
    </h3>

    <hr style="border:1px solid #2E3B55;">

    <p style="color:white;font-size:16px;">
    🌲 <b>Model:</b> Random Forest
    </p>

    <p style="color:white;font-size:16px;">
    💧 <b>Prediction:</b> Moisture Stress
    </p>

    <p style="color:white;font-size:16px;">
    🎯 <b>Accuracy:</b> 100%
    </p>

    <p style="color:white;font-size:16px;">
    🟢 <b>Status:</b> Production Ready
    </p>

    </div>
    """, unsafe_allow_html=True)

# ── Accuracy Gauge ─────────────────────────────────────────────────────────────
with right:
    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=100,
            title={"text": "Accuracy (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "limegreen"},
                "steps": [
                    {"range": [0, 50], "color": "#8B0000"},
                    {"range": [50, 80], "color": "orange"},
                    {"range": [80, 100], "color": "green"}
                ]
            }
        )
    )
    gauge.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        height=320,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(gauge, use_container_width=True)

st.markdown("---")

# ── Model Details ──────────────────────────────────────────────────────────────
st.markdown("### 📐 Model Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background:#16213E;padding:18px;border-radius:12px;border-left:5px solid #38bdf8;">
    <h4 style="color:white;">⚙️ Hyperparameters</h4>
    <p style="color:#cbd5e1;">• n_estimators: 100</p>
    <p style="color:#cbd5e1;">• max_depth: None (full trees)</p>
    <p style="color:#cbd5e1;">• random_state: 42</p>
    <p style="color:#cbd5e1;">• criterion: gini</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#16213E;padding:18px;border-radius:12px;border-left:5px solid #a78bfa;">
    <h4 style="color:white;">📊 Evaluation Metrics</h4>
    <p style="color:#cbd5e1;">• Accuracy: 100%</p>
    <p style="color:#cbd5e1;">• Precision: 1.00</p>
    <p style="color:#cbd5e1;">• Recall: 1.00</p>
    <p style="color:#cbd5e1;">• F1-Score: 1.00</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>",
    unsafe_allow_html=True
)
