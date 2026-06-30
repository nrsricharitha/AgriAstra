import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Weather – AgriAstra", page_icon="🌦️", layout="wide")

st.markdown("""
<style>
.stApp { background:#0b1220; color:#f8fafc; }
.block-container { padding-top:1.5rem; padding-bottom:1rem; }
h1,h2,h3,h4 { color:#ffffff; }
footer { visibility:hidden; }
.weather-card {
    background:#16213E;
    border-radius:14px;
    padding:18px;
    text-align:center;
    border-top:4px solid #38bdf8;
    box-shadow:0 4px 12px rgba(0,0,0,.4);
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🌦️ Weather Integration")
st.caption("Real-time weather conditions and 7-day forecast to enhance irrigation recommendations.")

# ── Location Selection ────────────────────────────────────────────────────────
locations = {
    "Nalgonda": (17.0575, 79.2671),
    "Miryalaguda": (16.8726, 79.5697),
    "Suryapet": (17.1399, 79.6215),
    "Bhongir": (17.5144, 78.8915),
    "Devarakonda": (16.6889, 79.5369),
    "Huzurnagar": (16.8976, 79.8852),
    "Nakrekal": (17.05, 79.32),
}

col_loc, col_btn = st.columns([3, 1])
with col_loc:
    selected_loc = st.selectbox("📍 Select Location in Nalgonda District", list(locations.keys()))
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    fetch_btn = st.button("🔄 Fetch Weather", type="primary", use_container_width=True)

lat, lon = locations[selected_loc]

# ── Fetch Weather from Open-Meteo (free, no API key) ─────────────────────────
@st.cache_data(ttl=1800)  # Cache 30 minutes
def fetch_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"precipitation,rain,wind_speed_10m,wind_direction_10m,cloud_cover,"
            f"weather_code,soil_moisture_0_to_1cm"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            f"rain_sum,et0_fao_evapotranspiration,precipitation_hours,"
            f"wind_speed_10m_max,weather_code"
            f"&timezone=Asia%2FKolkata"
            f"&forecast_days=7"
        )
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        return None

if fetch_btn or "weather_data" not in st.session_state or st.session_state.get("weather_loc") != selected_loc:
    with st.spinner(f"Fetching real-time weather for {selected_loc}..."):
        data = fetch_weather(lat, lon)
        st.session_state["weather_data"] = data
        st.session_state["weather_loc"] = selected_loc
else:
    data = st.session_state.get("weather_data")

# WMO weather code descriptions
WMO_CODES = {
    0: ("Clear Sky", "☀️"), 1: ("Mainly Clear", "🌤️"), 2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Icy Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"), 53: ("Moderate Drizzle", "🌦️"), 55: ("Heavy Drizzle", "🌧️"),
    61: ("Light Rain", "🌧️"), 63: ("Moderate Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"),
    80: ("Light Showers", "🌦️"), 81: ("Moderate Showers", "🌧️"), 82: ("Heavy Showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm+Hail", "⛈️"), 99: ("Severe Thunderstorm", "⛈️"),
}

if data and "current" in data:
    curr = data["current"]
    daily = data["daily"]
    
    temp = curr.get("temperature_2m", 0)
    humidity = curr.get("relative_humidity_2m", 0)
    feels_like = curr.get("apparent_temperature", 0)
    rain = curr.get("rain", 0)
    precip = curr.get("precipitation", 0)
    wind = curr.get("wind_speed_10m", 0)
    wind_dir = curr.get("wind_direction_10m", 0)
    cloud = curr.get("cloud_cover", 0)
    soil_moist = curr.get("soil_moisture_0_to_1cm", 0)
    wcode = curr.get("weather_code", 0)
    wx_desc, wx_emoji = WMO_CODES.get(wcode, ("Unknown", "🌡️"))

    st.markdown(f"### {wx_emoji} Current Conditions — {selected_loc}")
    st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}")

    # ── Current Weather Cards ─────────────────────────────────────────────────
    w1, w2, w3, w4, w5, w6 = st.columns(6)
    cards = [
        (w1, "🌡️", "Temperature", f"{temp:.1f}°C", f"Feels {feels_like:.1f}°C", "#ef4444"),
        (w2, "💧", "Humidity", f"{humidity}%", "Relative humidity", "#38bdf8"),
        (w3, "🌧️", "Rainfall", f"{precip:.1f}mm", "Today's total", "#60a5fa"),
        (w4, "💨", "Wind Speed", f"{wind:.1f} km/h", f"Direction {wind_dir}°", "#a78bfa"),
        (w5, "☁️", "Cloud Cover", f"{cloud}%", wx_desc, "#94a3b8"),
        (w6, "🌱", "Soil Moisture", f"{soil_moist:.3f}", "0–1cm depth", "#00b894"),
    ]
    for col, icon, label, val, sub, clr in cards:
        with col:
            st.markdown(f"""
            <div class="weather-card" style="border-top-color:{clr};">
            <p style="color:#94a3b8;font-size:12px;margin:0;">{icon} {label}</p>
            <p style="color:{clr};font-size:28px;font-weight:700;margin:6px 0;">{val}</p>
            <p style="color:#64748b;font-size:11px;margin:0;">{sub}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Irrigation Advisory based on Weather ──────────────────────────────────
    st.markdown("### 🚜 Weather-Enhanced Irrigation Advisory")

    # Combine weather with any existing field analysis
    field_result = st.session_state.get("field_result", {})
    stress = field_result.get("stress", "Moderate")

    # Rules engine
    rain_forecast_3d = sum(daily["precipitation_sum"][:3]) if daily.get("precipitation_sum") else 0
    et0 = daily["et0_fao_evapotranspiration"][0] if daily.get("et0_fao_evapotranspiration") else 0
    
    advisory_color = "#facc15"
    advisory_text = ""
    advisory_actions = []

    if rain_forecast_3d > 30:
        advisory_color = "#22c55e"
        advisory_text = f"✅ Sufficient rainfall expected ({rain_forecast_3d:.1f}mm over 3 days). No irrigation recommended."
        advisory_actions = [
            "🌧️ Wait for natural rainfall — expected to be adequate",
            "📊 Monitor soil moisture after rain event",
            "🌾 Focus on drainage management if rain is heavy",
        ]
    elif stress == "High" and rain_forecast_3d < 10:
        advisory_color = "#ef4444"
        advisory_text = f"🚨 CRITICAL: High crop stress + minimal rainfall forecast ({rain_forecast_3d:.1f}mm). Irrigate immediately."
        advisory_actions = [
            "💧 Irrigate within 24 hours — soil deficit is critical",
            f"📐 Apply {et0*1.2:.0f}–{et0*1.5:.0f}mm water based on ET₀={et0:.1f}mm/day",
            "🌡️ Consider morning irrigation to reduce evaporation losses",
            "📡 Re-check Sentinel-2 NDVI in 5–7 days post-irrigation",
        ]
    elif stress == "Moderate" and rain_forecast_3d < 20:
        advisory_color = "#facc15"
        advisory_text = f"⚠️ Moderate stress + limited rainfall ({rain_forecast_3d:.1f}mm forecast). Schedule irrigation in 2–3 days."
        advisory_actions = [
            "💧 Plan irrigation within 48–72 hours",
            f"📐 Apply {et0:.0f}–{et0*1.2:.0f}mm water (ET₀={et0:.1f}mm/day)",
            "🌧️ Monitor actual rainfall before irrigating",
        ]
    else:
        advisory_color = "#22c55e"
        advisory_text = "✅ Current conditions are manageable. Continue routine monitoring."
        advisory_actions = [
            "📊 Weekly satellite monitoring recommended",
            "🌱 Crop appears adequately irrigated given weather",
        ]

    st.markdown(f"""
    <div style="background:#16213E;border-radius:14px;padding:20px;border-left:6px solid {advisory_color};margin-bottom:16px;">
    <h4 style="color:{advisory_color};margin-top:0;">Weather-Enhanced Recommendation</h4>
    <p style="color:#f8fafc;font-size:16px;margin-bottom:10px;">{advisory_text}</p>
    {"".join([f'<p style="color:#cbd5e1;font-size:14px;margin:4px 0;">• {a}</p>' for a in advisory_actions])}
    <p style="color:#64748b;font-size:12px;margin-top:12px;">
    📊 Based on: {stress} stress level · {rain_forecast_3d:.1f}mm 3-day forecast · ET₀={et0:.1f}mm/day
    </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 7-Day Forecast Chart ──────────────────────────────────────────────────
    st.markdown("### 📅 7-Day Forecast")

    dates = [datetime.now() + timedelta(days=i) for i in range(7)]
    date_labels = [d.strftime("%a\n%d %b") for d in dates]
    
    temp_max = daily.get("temperature_2m_max", [0]*7)
    temp_min = daily.get("temperature_2m_min", [0]*7)
    rain_daily = daily.get("precipitation_sum", [0]*7)
    et0_daily = daily.get("et0_fao_evapotranspiration", [0]*7)
    wcodes = daily.get("weather_code", [0]*7)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=date_labels, y=rain_daily, name="Rainfall (mm)",
        marker_color="#38bdf8", opacity=0.8, yaxis="y2"
    ))
    fig.add_trace(go.Scatter(
        x=date_labels, y=temp_max, name="Max Temp (°C)",
        line=dict(color="#ef4444", width=2), mode="lines+markers",
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=date_labels, y=temp_min, name="Min Temp (°C)",
        line=dict(color="#60a5fa", width=2, dash="dot"), mode="lines+markers",
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=date_labels, y=et0_daily, name="ET₀ (mm/day)",
        line=dict(color="#00b894", width=2, dash="dash"), mode="lines+markers",
        marker=dict(size=7)
    ))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0b1220", plot_bgcolor="#0b1220",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Temperature / ET₀", color="#94a3b8"),
        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right", color="#38bdf8"),
        height=350, margin=dict(l=20, r=60, t=30, b=40),
        xaxis=dict(color="#f8fafc")
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Day-by-Day Forecast Cards ─────────────────────────────────────────────
    st.markdown("### 🗓️ Daily Forecast")
    cols = st.columns(7)
    for i, (col, date) in enumerate(zip(cols, dates)):
        wc = wcodes[i] if i < len(wcodes) else 0
        wx_d, wx_e = WMO_CODES.get(wc, ("?","🌡️"))
        r = rain_daily[i] if i < len(rain_daily) else 0
        tmax = temp_max[i] if i < len(temp_max) else 0
        tmin = temp_min[i] if i < len(temp_min) else 0
        rain_color = "#38bdf8" if r > 20 else "#60a5fa" if r > 5 else "#64748b"
        with col:
            st.markdown(f"""
            <div style="background:#16213E;border-radius:12px;padding:12px;text-align:center;">
            <p style="color:#94a3b8;font-size:11px;margin:0;">{date.strftime('%a')}</p>
            <p style="color:#64748b;font-size:10px;margin:0;">{date.strftime('%d %b')}</p>
            <p style="font-size:24px;margin:6px 0;">{wx_e}</p>
            <p style="color:#ef4444;font-size:13px;font-weight:600;margin:0;">{tmax:.0f}°</p>
            <p style="color:#60a5fa;font-size:12px;margin:2px 0;">{tmin:.0f}°</p>
            <p style="color:{rain_color};font-size:12px;margin:4px 0;">💧{r:.1f}mm</p>
            </div>
            """, unsafe_allow_html=True)

else:
    st.warning("⚠️ Unable to fetch weather data. Check your internet connection or try again.")
    st.info("AgriAstra uses Open-Meteo API (free, no API key required) for real-time weather data.")
    
    # Show demo data
    st.markdown("### 📊 Sample Data (Demo Mode)")
    demo = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Max Temp (°C)": [34, 33, 35, 36, 32, 31, 33],
        "Min Temp (°C)": [24, 23, 25, 26, 22, 21, 23],
        "Rainfall (mm)": [0, 5, 0, 0, 12, 8, 0],
    })
    st.dataframe(demo, use_container_width=True)

st.markdown("---")
st.markdown("<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>", unsafe_allow_html=True)
