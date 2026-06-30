import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Explainable AI – AgriAstra", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.stApp { background:#0b1220; color:#f8fafc; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
h1,h2,h3,h4 { color:#ffffff; }
footer { visibility:hidden; }
.explain-card {
    background:#16213E;
    border-radius:14px;
    padding:18px;
    margin-bottom:14px;
    border-left:5px solid #a78bfa;
    box-shadow:0 4px 12px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/agriastra_final_dataset.csv")

@st.cache_resource
def train_model(df):
    le = LabelEncoder()
    X = df[["NDVI", "NDWI", "VH", "VV", "Rainfall"]]
    y = le.fit_transform(df["Moisture_Stress"])
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    return model, le, X

df = load_data()
model, le, X_train = train_model(df)

FEATURE_NAMES = ["NDVI", "NDWI", "VH", "VV", "Rainfall"]

FEATURE_DESCRIPTIONS = {
    "NDVI": {
        "full": "Normalized Difference Vegetation Index",
        "desc": "Measures vegetation greenness and health from Sentinel-2 imagery.",
        "high": "🌿 Dense/healthy vegetation",
        "low": "🏜️ Sparse/stressed vegetation",
        "range": "[-1, 1]",
        "color": "#00b894",
        "icon": "🌱"
    },
    "NDWI": {
        "full": "Normalized Difference Water Index",
        "desc": "Measures water content in vegetation canopy from Sentinel-2.",
        "high": "💧 High water content in leaves",
        "low": "🥵 Low water content (drought stress)",
        "range": "[-1, 1]",
        "color": "#38bdf8",
        "icon": "💧"
    },
    "VH": {
        "full": "Sentinel-1 VH SAR Backscatter",
        "desc": "Vertical-Horizontal polarization radar backscatter — sensitive to crop structure and soil moisture.",
        "high": "🌾 Dense canopy / wet soil",
        "low": "🏗️ Bare soil / dry conditions",
        "range": "[-35, -10] dB",
        "color": "#a78bfa",
        "icon": "📡"
    },
    "VV": {
        "full": "Sentinel-1 VV SAR Backscatter",
        "desc": "Vertical-Vertical polarization — sensitive to surface roughness and moisture.",
        "high": "🌊 High surface moisture",
        "low": "🪨 Low surface moisture",
        "range": "[-27, -3] dB",
        "color": "#fb923c",
        "icon": "📡"
    },
    "Rainfall": {
        "full": "Monthly Rainfall (CHIRPS)",
        "desc": "Monthly precipitation from Climate Hazards Group InfraRed Precipitation with Station data.",
        "high": "🌧️ Adequate/excess rainfall",
        "low": "☀️ Rainfall deficit",
        "range": "[0, ∞] mm",
        "color": "#60a5fa",
        "icon": "🌧️"
    }
}

st.markdown("## 🤖 Explainable AI — Why This Prediction?")
st.caption("AgriAstra doesn't just predict — it explains. Understand which satellite parameters drive each irrigation decision.")

# ── Input Parameters ──────────────────────────────────────────────────────────
with st.expander("🛰️ Input Satellite Parameters", expanded=True):
    # Pre-fill from field analysis if available
    defaults = st.session_state.get("field_result", {})
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        ndvi = st.slider("🌱 NDVI", -0.5, 1.0, float(defaults.get("ndvi", 0.45)), 0.01)
    with c2:
        ndwi = st.slider("💧 NDWI", -0.8, 0.7, float(defaults.get("ndwi", -0.52)), 0.01)
    with c3:
        vh = st.slider("📡 VH", -35.0, -10.0, float(defaults.get("vh", -18.9)), 0.1)
    with c4:
        vv = st.slider("📡 VV", -27.0, -3.0, float(defaults.get("vv", -11.5)), 0.1)
    with c5:
        rainfall = st.slider("🌧️ Rainfall", 0.0, 100.0, float(defaults.get("rainfall", 18.5)), 0.5)

X_input = np.array([[ndvi, ndwi, vh, vv, rainfall]])
pred_encoded = model.predict(X_input)[0]
pred_label = le.inverse_transform([pred_encoded])[0]
pred_proba = model.predict_proba(X_input)[0]
classes = le.inverse_transform(range(len(le.classes_)))
proba_dict = dict(zip(classes, pred_proba))

# ── Feature importances (global) & local approximation ───────────────────────
global_importance = model.feature_importances_

# Local feature contribution via mean decrease approach
# Compare prediction confidence when each feature is set to its mean
base_conf = max(pred_proba)
local_contributions = []
for i, feat in enumerate(FEATURE_NAMES):
    X_perturbed = X_input.copy()
    X_perturbed[0, i] = X_train[feat].mean()
    perturbed_proba = model.predict_proba(X_perturbed)[0]
    perturbed_conf = perturbed_proba[pred_encoded]
    # How much does this feature contribute to current class confidence?
    contribution = pred_proba[pred_encoded] - perturbed_conf
    local_contributions.append(contribution)

local_contributions = np.array(local_contributions)

# ── Prediction Result Banner ──────────────────────────────────────────────────
stress_map = {
    "Low": ("#22c55e", "🟢", "No irrigation needed", "Crop is healthy. The vegetation indices confirm adequate water availability."),
    "Moderate": ("#facc15", "🟡", "Irrigate within 3 days", "Moderate water deficit detected. Satellite data shows beginning signs of stress."),
    "High": ("#ef4444", "🔴", "Irrigate immediately", "Critical moisture deficit. Multiple indices confirm severe crop stress.")
}
color, emoji, advisory, summary = stress_map.get(pred_label, ("#94a3b8","⚪","Unknown",""))

st.markdown(f"""
<div style="background:linear-gradient(135deg,#16213E,#1e293b);border-radius:16px;padding:24px;border:2px solid {color};margin:16px 0;">
<div style="display:flex;align-items:center;gap:16px;">
<div style="font-size:48px;">{emoji}</div>
<div>
<h2 style="color:{color};margin:0;">{pred_label} Moisture Stress</h2>
<p style="color:#38bdf8;font-size:18px;margin:4px 0;">🚜 {advisory}</p>
<p style="color:#cbd5e1;margin:4px 0;">{summary}</p>
<p style="color:#64748b;font-size:13px;margin:0;">Model confidence: <b style="color:{color};">{max(pred_proba)*100:.1f}%</b></p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── Why This Prediction ───────────────────────────────────────────────────────
st.markdown("### 🔍 Why Did AgriAstra Predict This?")
st.markdown("Each satellite parameter below shows how it influenced the prediction:")

# Sort by absolute local contribution
sorted_feats = sorted(zip(FEATURE_NAMES, local_contributions, global_importance), key=lambda x: abs(x[1]), reverse=True)

for rank, (feat, local_c, global_imp) in enumerate(sorted_feats):
    info = FEATURE_DESCRIPTIONS[feat]
    direction = "▲ INCREASED" if local_c > 0 else "▼ DECREASED"
    dir_color = color if local_c > 0 else "#64748b"
    
    current_val = X_input[0, FEATURE_NAMES.index(feat)]
    mean_val = X_train[feat].mean()
    is_above_mean = current_val > mean_val
    
    # Plain-English explanation
    if feat == "NDVI":
        if pred_label == "High" and current_val < 0.3:
            explanation = f"Your NDVI ({current_val:.3f}) is below the healthy threshold (~0.5), indicating sparse or stressed vegetation — a strong signal of drought stress."
        elif pred_label == "Low" and current_val > 0.6:
            explanation = f"High NDVI ({current_val:.3f}) confirms healthy, dense vegetation with adequate photosynthetic activity."
        else:
            explanation = f"NDVI ({current_val:.3f}) is moderate — vegetation shows some signs of stress but is not critical."
    elif feat == "NDWI":
        if current_val < -0.5:
            explanation = f"Low NDWI ({current_val:.3f}) indicates water deficit in the crop canopy — leaves are losing turgor pressure."
        elif current_val > -0.2:
            explanation = f"NDWI ({current_val:.3f}) suggests adequate water content in vegetation canopy."
        else:
            explanation = f"NDWI ({current_val:.3f}) shows moderate water content, consistent with early-stage stress."
    elif feat in ["VH", "VV"]:
        if current_val < mean_val:
            explanation = f"SAR backscatter ({current_val:.1f} dB) is lower than average ({mean_val:.1f} dB), suggesting reduced canopy density or lower soil moisture."
        else:
            explanation = f"SAR backscatter ({current_val:.1f} dB) is above average — indicating denser canopy or wetter soil conditions."
    else:  # Rainfall
        explanation = f"Monthly CHIRPS rainfall of {current_val:.1f}mm for the study area — this is the baseline precipitation input for the model."

    badge = f"#{rank+1} Most Influential"
    
    st.markdown(f"""
    <div style="background:#16213E;border-radius:12px;padding:16px;margin-bottom:10px;border-left:5px solid {info['color']};">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
    <div>
        <span style="font-size:18px;">{info['icon']}</span>
        <span style="color:white;font-size:16px;font-weight:700;margin-left:8px;">{feat}</span>
        <span style="background:#0f172a;color:#94a3b8;font-size:11px;padding:2px 10px;border-radius:10px;margin-left:8px;">{badge}</span>
    </div>
    <div>
        <span style="color:{info['color']};font-size:20px;font-weight:700;">{current_val:.3f}</span>
        <span style="color:#64748b;font-size:13px;margin-left:6px;">vs avg {mean_val:.3f}</span>
    </div>
    </div>
    <p style="color:#94a3b8;font-size:12px;margin:8px 0 4px 0;">{info['full']} — {info['desc']}</p>
    <p style="color:#e2e8f0;font-size:14px;margin:6px 0;">💬 <b>Explanation:</b> {explanation}</p>
    <div style="display:flex;gap:20px;margin-top:8px;">
    <span style="color:{dir_color};font-size:12px;font-weight:600;">{direction} stress confidence by {abs(local_c)*100:.1f}%</span>
    <span style="color:#64748b;font-size:12px;">Global importance: {global_imp*100:.1f}%</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ── Feature Importance Charts ─────────────────────────────────────────────────
st.markdown("### 📊 Feature Importance Analysis")
ch1, ch2 = st.columns(2)

with ch1:
    fig_global = go.Figure(go.Bar(
        x=[f*100 for f in global_importance],
        y=FEATURE_NAMES,
        orientation='h',
        marker=dict(
            color=[FEATURE_DESCRIPTIONS[f]['color'] for f in FEATURE_NAMES],
            line=dict(width=0)
        ),
        text=[f"{f*100:.1f}%" for f in global_importance],
        textposition='outside',
        textfont=dict(color='white', size=11)
    ))
    fig_global.update_layout(
        title=dict(text="🌐 Global Feature Importance (All Predictions)", font=dict(color='white')),
        template="plotly_dark", paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
        xaxis=dict(title="Importance (%)", color='#94a3b8', range=[0, max(global_importance)*130]),
        yaxis=dict(color='white'),
        height=280, margin=dict(l=10, r=60, t=50, b=30)
    )
    st.plotly_chart(fig_global, use_container_width=True)

with ch2:
    lc_colors = [color if c > 0 else "#64748b" for c in local_contributions]
    fig_local = go.Figure(go.Bar(
        x=[c*100 for c in local_contributions],
        y=FEATURE_NAMES,
        orientation='h',
        marker=dict(color=lc_colors),
        text=[f"{c*100:+.1f}%" for c in local_contributions],
        textposition='outside',
        textfont=dict(color='white', size=11)
    ))
    fig_local.update_layout(
        title=dict(text=f"🎯 Local Contribution (This Prediction: {pred_label})", font=dict(color='white')),
        template="plotly_dark", paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
        xaxis=dict(title="Confidence Change (%)", color='#94a3b8'),
        yaxis=dict(color='white'),
        height=280, margin=dict(l=10, r=60, t=50, b=30)
    )
    st.plotly_chart(fig_local, use_container_width=True)

# ── Suggested Actions ─────────────────────────────────────────────────────────
st.markdown("### 🌾 Suggested Actions")

actions_map = {
    "High": [
        ("🚨 Irrigate Immediately", "Apply 60–80mm water within 24 hours. Crop damage risk is high.", "#ef4444"),
        ("📡 Cross-check SAR data", "Verify VH/VV values with Sentinel-1 GRD product from last 6 days.", "#a78bfa"),
        ("🌱 Monitor NDVI Recovery", "Re-acquire Sentinel-2 imagery in 5–7 days after irrigation.", "#00b894"),
        ("📋 Alert Farmer", "Send SMS/WhatsApp notification to farmer about critical irrigation need.", "#38bdf8"),
    ],
    "Moderate": [
        ("💧 Schedule Irrigation", "Plan irrigation within 3 days. Apply 40–60mm water.", "#facc15"),
        ("📊 Monitor Closely", "Increase monitoring frequency — check satellite data every 3 days.", "#00b894"),
        ("🌧️ Check Forecast", "Verify 5-day rainfall forecast before irrigation to avoid over-watering.", "#38bdf8"),
        ("📝 Document Condition", "Log current field state for seasonal comparison.", "#a78bfa"),
    ],
    "Low": [
        ("✅ Maintain Practice", "No irrigation needed. Current crop management is adequate.", "#22c55e"),
        ("📅 Routine Monitoring", "Schedule next satellite analysis in 7–10 days.", "#00b894"),
        ("🌾 Crop Health Check", "Visually inspect field for pest/disease if NDVI seems unusually high.", "#facc15"),
        ("📊 Record Baseline", "Save current indices as baseline for this growth stage.", "#38bdf8"),
    ]
}
actions = actions_map.get(pred_label, [])

ac1, ac2 = st.columns(2)
for i, (action_title, action_desc, action_color) in enumerate(actions):
    with (ac1 if i % 2 == 0 else ac2):
        st.markdown(f"""
        <div style="background:#16213E;border-radius:12px;padding:14px;margin-bottom:10px;border-left:4px solid {action_color};">
        <p style="color:{action_color};font-weight:700;font-size:15px;margin:0 0 4px 0;">{action_title}</p>
        <p style="color:#cbd5e1;font-size:13px;margin:0;">{action_desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>", unsafe_allow_html=True)
