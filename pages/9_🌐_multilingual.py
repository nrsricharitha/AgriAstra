import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Multilingual – AgriAstra", page_icon="🌐", layout="wide")

st.markdown("""
<style>
.stApp { background:#0b1220; color:#f8fafc; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
h1,h2,h3,h4 { color:#ffffff; }
footer { visibility:hidden; }
.lang-card { background:#16213E; border-radius:14px; padding:20px; margin-bottom:14px; }
</style>
""", unsafe_allow_html=True)

# ── All translations ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "title": "🌾 Field Analysis & Irrigation Advisory",
        "subtitle": "AI-powered crop monitoring for Nalgonda District",
        "select_lang": "Select Language",
        "parameters": "Satellite Parameters",
        "ndvi_label": "🌱 NDVI (Vegetation Index)",
        "ndwi_label": "💧 NDWI (Water Index)",
        "rainfall_label": "🌧️ Monthly Rainfall (mm)",
        "analyze_btn": "🔍 Analyze Field",
        "result_title": "📊 Analysis Result",
        "stress_label": "Moisture Stress Level",
        "advisory_label": "Irrigation Advisory",
        "confidence_label": "Model Confidence",
        "advisories": {
            "Low": "✅ No irrigation needed. Your crop is healthy!",
            "Moderate": "⚠️ Please irrigate within 3 days.",
            "High": "🚨 Critical! Irrigate your field immediately.",
        },
        "actions": {
            "Low": ["✅ Crop is healthy — continue current practices", "📅 Next check in 7–10 days", "📊 Monitor rainfall forecast weekly"],
            "Moderate": ["💧 Plan irrigation within 2–3 days", "🌱 Apply 40–60mm water based on soil type", "📊 Monitor soil moisture closely"],
            "High": ["🚨 Irrigate immediately to prevent crop loss", "💧 Apply 60–80mm water urgently", "📡 Re-check satellite data in 5 days"],
        },
        "data_source": "📡 Data: Sentinel-1/2 Satellite + CHIRPS Rainfall | Model: Random Forest",
        "footer": "🌾 AgriAstra | Precision Agriculture using AI + GIS",
        "what_means": "What does this mean?",
        "low_exp": "Your crops have sufficient water. The vegetation index (NDVI) and water index (NDWI) show healthy levels.",
        "mod_exp": "Your crops are showing early signs of water stress. Irrigation in the next few days will prevent yield loss.",
        "high_exp": "Your crops are severely stressed for water. Immediate irrigation is necessary to save the crop.",
    },
    "తెలుగు": {
        "title": "🌾 పొల విశ్లేషణ & నీటిపారుదల సలహా",
        "subtitle": "నల్గొండ జిల్లాలో AI ఆధారిత పంట పర్యవేక్షణ",
        "select_lang": "భాష ఎంచుకోండి",
        "parameters": "ఉపగ్రహ పారామితులు",
        "ndvi_label": "🌱 NDVI (వృక్ష సూచిక)",
        "ndwi_label": "💧 NDWI (నీటి సూచిక)",
        "rainfall_label": "🌧️ నెలవారీ వర్షపాతం (మి.మీ)",
        "analyze_btn": "🔍 పొలాన్ని విశ్లేషించు",
        "result_title": "📊 విశ్లేషణ ఫలితం",
        "stress_label": "తేమ ఒత్తిడి స్థాయి",
        "advisory_label": "నీటిపారుదల సలహా",
        "confidence_label": "మోడల్ విశ్వాసం",
        "advisories": {
            "Low": "✅ నీటిపారుదల అవసరం లేదు. మీ పంట ఆరోగ్యంగా ఉంది!",
            "Moderate": "⚠️ దయచేసి 3 రోజులలోపు నీటిపారుదల చేయండి.",
            "High": "🚨 అత్యవసరం! వెంటనే మీ పొలానికి నీరు పెట్టండి.",
        },
        "actions": {
            "Low": ["✅ పంట ఆరోగ్యంగా ఉంది — ప్రస్తుత పద్ధతులు కొనసాగించండి", "📅 7–10 రోజులలో తదుపరి తనిఖీ", "📊 వారపు వర్షపాత అంచనా చూడండి"],
            "Moderate": ["💧 2–3 రోజులలో నీటిపారుదల ప్లాన్ చేయండి", "🌱 నేల రకాన్ని బట్టి 40–60 మి.మీ. నీరు వేయండి", "📊 నేల తేమను నిశితంగా పర్యవేక్షించండి"],
            "High": ["🚨 పంట నష్టాన్ని నివారించడానికి వెంటనే నీరు పెట్టండి", "💧 తక్షణమే 60–80 మి.మీ. నీరు వేయండి", "📡 5 రోజులలో మళ్ళీ ఉపగ్రహ డేటా తనిఖీ చేయండి"],
        },
        "data_source": "📡 డేటా: Sentinel-1/2 ఉపగ్రహం + CHIRPS వర్షపాతం | మోడల్: Random Forest",
        "footer": "🌾 AgriAstra | AI + GIS ఆధారిత ఖచ్చితమైన వ్యవసాయం",
        "what_means": "ఇది ఏమి అర్థమవుతుంది?",
        "low_exp": "మీ పంటలకు తగినంత నీరు ఉంది. NDVI మరియు NDWI సూచికలు ఆరోగ్యకరమైన స్థాయిలను చూపిస్తున్నాయి.",
        "mod_exp": "మీ పంటలు తొలి దశలో నీటి ఒత్తిడి చూపిస్తున్నాయి. కొద్ది రోజులలో నీటిపారుదల దిగుబడి నష్టాన్ని నివారిస్తుంది.",
        "high_exp": "మీ పంటలకు నీటి కొరత తీవ్రంగా ఉంది. పంటను రక్షించడానికి తక్షణ నీటిపారుదల అవసరం.",
    },
    "हिंदी": {
        "title": "🌾 खेत विश्लेषण और सिंचाई सलाह",
        "subtitle": "नलगोंडा जिले के लिए AI आधारित फसल निगरानी",
        "select_lang": "भाषा चुनें",
        "parameters": "उपग्रह पैरामीटर",
        "ndvi_label": "🌱 NDVI (वनस्पति सूचकांक)",
        "ndwi_label": "💧 NDWI (जल सूचकांक)",
        "rainfall_label": "🌧️ मासिक वर्षा (मिमी)",
        "analyze_btn": "🔍 खेत का विश्लेषण करें",
        "result_title": "📊 विश्लेषण परिणाम",
        "stress_label": "नमी तनाव स्तर",
        "advisory_label": "सिंचाई सलाह",
        "confidence_label": "मॉडल विश्वास",
        "advisories": {
            "Low": "✅ सिंचाई की आवश्यकता नहीं है। आपकी फसल स्वस्थ है!",
            "Moderate": "⚠️ कृपया 3 दिनों के भीतर सिंचाई करें।",
            "High": "🚨 आपातकाल! तुरंत अपने खेत में पानी दें।",
        },
        "actions": {
            "Low": ["✅ फसल स्वस्थ है — वर्तमान प्रथाएं जारी रखें", "📅 7–10 दिनों में अगली जांच", "📊 साप्ताहिक वर्षा पूर्वानुमान देखें"],
            "Moderate": ["💧 2–3 दिनों में सिंचाई की योजना बनाएं", "🌱 मिट्टी के प्रकार के आधार पर 40–60 मिमी पानी डालें", "📊 मिट्टी की नमी की बारीकी से निगरानी करें"],
            "High": ["🚨 फसल नुकसान को रोकने के लिए तुरंत सिंचाई करें", "💧 तत्काल 60–80 मिमी पानी डालें", "📡 5 दिनों में उपग्रह डेटा फिर से जांचें"],
        },
        "data_source": "📡 डेटा: Sentinel-1/2 उपग्रह + CHIRPS वर्षा | मॉडल: Random Forest",
        "footer": "🌾 AgriAstra | AI + GIS आधारित सटीक कृषि",
        "what_means": "इसका क्या मतलब है?",
        "low_exp": "आपकी फसलों में पर्याप्त पानी है। NDVI और NDWI सूचकांक स्वस्थ स्तर दिखा रहे हैं।",
        "mod_exp": "आपकी फसलें प्रारंभिक जल तनाव के संकेत दिखा रही हैं। कुछ दिनों में सिंचाई उपज हानि को रोकेगी।",
        "high_exp": "आपकी फसलें गंभीर जल तनाव में हैं। फसल बचाने के लिए तत्काल सिंचाई आवश्यक है।",
    }
}

# ── Language Selection ────────────────────────────────────────────────────────
lang_options = list(TRANSLATIONS.keys())
lang_flags = {"English": "🇬🇧", "తెలుగు": "🇮🇳", "हिंदी": "🇮🇳"}

sel_lang = st.selectbox(
    "🌐 Select Language / భాష ఎంచుకోండి / भाषा चुनें",
    lang_options,
    format_func=lambda x: f"{lang_flags.get(x,'🌐')} {x}"
)

T = TRANSLATIONS[sel_lang]

st.markdown(f"## {T['title']}")
st.caption(T['subtitle'])

st.markdown("---")

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/agriastra_final_dataset.csv")

@st.cache_resource
def train_model():
    df = load_data()
    le = LabelEncoder()
    X = df[["NDVI","NDWI","VH","VV","Rainfall"]]
    y = le.fit_transform(df["Moisture_Stress"])
    m = RandomForestClassifier(n_estimators=100, random_state=42)
    m.fit(X, y)
    return m, le

model, le = train_model()

# ── Input Parameters ──────────────────────────────────────────────────────────
st.markdown(f"### 🛰️ {T['parameters']}")
defaults = st.session_state.get("field_result", {})

p1, p2, p3 = st.columns(3)
with p1:
    ndvi = st.slider(T['ndvi_label'], -0.5, 1.0, float(defaults.get("ndvi", 0.45)), 0.01)
with p2:
    ndwi = st.slider(T['ndwi_label'], -0.8, 0.7, float(defaults.get("ndwi", -0.52)), 0.01)
with p3:
    rainfall = st.slider(T['rainfall_label'], 0.0, 100.0, float(defaults.get("rainfall", 18.5)), 0.5)

vh = defaults.get("vh", -18.9)
vv = defaults.get("vv", -11.5)

if st.button(T['analyze_btn'], type="primary", use_container_width=True):
    X_input = np.array([[ndvi, ndwi, vh, vv, rainfall]])
    pred_enc = model.predict(X_input)[0]
    pred_label = le.inverse_transform([pred_enc])[0]
    pred_proba = model.predict_proba(X_input)[0]

    stress_colors = {"Low": "#22c55e", "Moderate": "#facc15", "High": "#ef4444"}
    stress_icons  = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
    color = stress_colors.get(pred_label, "#94a3b8")
    icon  = stress_icons.get(pred_label, "⚪")

    advisory_text = T['advisories'].get(pred_label, "")
    exp_text = T.get(f"{pred_label.lower()}_exp", "")
    actions = T['actions'].get(pred_label, [])

    st.markdown(f"## {T['result_title']}")
    
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div style="background:#16213E;border-radius:14px;padding:20px;text-align:center;border-left:6px solid {color};">
        <p style="color:#94a3b8;font-size:13px;margin:0;">{T['stress_label']}</p>
        <p style="color:{color};font-size:40px;font-weight:700;margin:8px 0;">{icon} {pred_label}</p>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div style="background:#16213E;border-radius:14px;padding:20px;text-align:center;border-left:6px solid #38bdf8;">
        <p style="color:#94a3b8;font-size:13px;margin:0;">{T['advisory_label']}</p>
        <p style="color:#38bdf8;font-size:16px;font-weight:700;margin:8px 0;">{advisory_text}</p>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
        <div style="background:#16213E;border-radius:14px;padding:20px;text-align:center;border-left:6px solid #a78bfa;">
        <p style="color:#94a3b8;font-size:13px;margin:0;">{T['confidence_label']}</p>
        <p style="color:#a78bfa;font-size:32px;font-weight:700;margin:8px 0;">{max(pred_proba)*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Explanation
    st.markdown(f"""
    <div style="background:#16213E;border-radius:12px;padding:16px;margin:14px 0;border-left:5px solid {color};">
    <h4 style="color:{color};margin-top:0;">💬 {T['what_means']}</h4>
    <p style="color:#cbd5e1;font-size:15px;margin:0;">{exp_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # Actions
    for action in actions:
        st.markdown(f"""
        <div style="background:#0f172a;border-radius:8px;padding:10px 14px;margin:6px 0;border-left:3px solid {color};">
        <p style="color:#e2e8f0;font-size:14px;margin:0;">{action}</p>
        </div>
        """, unsafe_allow_html=True)

    st.caption(T['data_source'])

st.markdown("---")
st.markdown(f"<center><h4>{T['footer']}</h4></center>", unsafe_allow_html=True)
