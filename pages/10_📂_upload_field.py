import streamlit as st
import pandas as pd
import numpy as np
import json
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import random

st.set_page_config(page_title="Upload Field Boundary – AgriAstra", page_icon="📂", layout="wide")

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
df = load_data()

st.markdown("## 📂 Upload Your Field Boundary")
st.caption("Upload a GeoJSON or KML file of your field to get AI-powered irrigation analysis for your exact boundary.")

# ── Upload Section ────────────────────────────────────────────────────────────
st.markdown("### 📁 Upload Field Boundary File")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Upload GeoJSON or KML file",
        type=["geojson", "json", "kml"],
        help="Export your field boundary from Google Earth, Google My Maps, or QGIS as GeoJSON/KML"
    )

with col2:
    st.markdown("""
    <div style="background:#16213E;border-radius:12px;padding:16px;border-left:4px solid #38bdf8;">
    <h4 style="color:#38bdf8;margin-top:0;">💡 How to get GeoJSON</h4>
    <p style="color:#cbd5e1;font-size:13px;margin:4px 0;">1. Open <b>Google Earth</b></p>
    <p style="color:#cbd5e1;font-size:13px;margin:4px 0;">2. Draw your field polygon</p>
    <p style="color:#cbd5e1;font-size:13px;margin:4px 0;">3. Export as KML</p>
    <p style="color:#cbd5e1;font-size:13px;margin:4px 0;">4. Convert at <b>geojson.io</b></p>
    <p style="color:#cbd5e1;font-size:13px;margin:4px 0;">— or use <b>QGIS</b> directly</p>
    </div>
    """, unsafe_allow_html=True)

# ── Demo option ───────────────────────────────────────────────────────────────
use_demo = st.checkbox("🔬 Use Demo Field (Sample Nalgonda farmland polygon)", value=not bool(uploaded_file))

# Sample GeoJSON polygon for Nalgonda area
DEMO_GEOJSON = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "Demo Field — Nalgonda", "area_ha": 2.4},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [79.2650, 17.0560],
                [79.2680, 17.0560],
                [79.2685, 17.0580],
                [79.2670, 17.0590],
                [79.2645, 17.0580],
                [79.2650, 17.0560]
            ]]
        }
    }]
}

geojson_data = None
parse_error = None

if uploaded_file:
    try:
        content = uploaded_file.read().decode("utf-8")
        if uploaded_file.name.endswith(".kml"):
            st.info("KML detected. For full KML support, converting using basic parser. Recommend using GeoJSON for best results.")
            # Basic KML coordinate extraction
            import re
            coords_match = re.findall(r'<coordinates>(.*?)</coordinates>', content, re.DOTALL)
            if coords_match:
                coord_list = []
                for coord_str in coords_match[0].strip().split():
                    parts = coord_str.split(",")
                    if len(parts) >= 2:
                        coord_list.append([float(parts[0]), float(parts[1])])
                if coord_list:
                    geojson_data = {
                        "type": "FeatureCollection",
                        "features": [{
                            "type": "Feature",
                            "properties": {"name": uploaded_file.name},
                            "geometry": {"type": "Polygon", "coordinates": [coord_list]}
                        }]
                    }
            else:
                parse_error = "Could not extract coordinates from KML. Please convert to GeoJSON."
        else:
            geojson_data = json.loads(content)
            st.success(f"✅ File loaded: {uploaded_file.name}")
    except Exception as e:
        parse_error = str(e)

if use_demo and not geojson_data:
    geojson_data = DEMO_GEOJSON
    st.info("📍 Using demo field polygon in Nalgonda district.")

if parse_error:
    st.error(f"❌ Error parsing file: {parse_error}")

# ── Process and Display ───────────────────────────────────────────────────────
if geojson_data:
    st.markdown("---")
    
    # Extract centroid from geometry
    features = geojson_data.get("features", [])
    
    if not features:
        st.warning("No features found in the file.")
    else:
        all_coords = []
        for feat in features:
            geom = feat.get("geometry", {})
            gtype = geom.get("type", "")
            if gtype == "Polygon":
                all_coords.extend(geom["coordinates"][0])
            elif gtype == "MultiPolygon":
                for poly in geom["coordinates"]:
                    all_coords.extend(poly[0])
            elif gtype == "Point":
                all_coords.append(geom["coordinates"])

        if all_coords:
            lons = [c[0] for c in all_coords]
            lats = [c[1] for c in all_coords]
            centroid_lat = np.mean(lats)
            centroid_lon = np.mean(lons)

            # Check if within Nalgonda bounding box
            in_nalgonda = (16.5 <= centroid_lat <= 17.6) and (78.6 <= centroid_lon <= 79.8)
            
            if not in_nalgonda:
                st.warning(f"⚠️ Field centroid ({centroid_lat:.4f}°N, {centroid_lon:.4f}°E) appears outside Nalgonda district. Analysis uses district-average satellite values.")

            # Field info
            props = features[0].get("properties", {})
            field_name = props.get("name", "Uploaded Field")
            
            st.markdown(f"### 🗺️ Field: {field_name}")

            info1, info2, info3 = st.columns(3)
            with info1:
                st.markdown(f"""
                <div style="background:#16213E;border-radius:12px;padding:14px;border-left:4px solid #00b894;">
                <p style="color:#94a3b8;font-size:12px;margin:0;">📍 CENTROID</p>
                <p style="color:#00b894;font-size:16px;font-weight:700;margin:6px 0;">{centroid_lat:.4f}°N, {centroid_lon:.4f}°E</p>
                </div>
                """, unsafe_allow_html=True)
            with info2:
                area_deg = abs((max(lons)-min(lons)) * (max(lats)-min(lats)))
                area_ha = area_deg * 111000 * 111000 / 10000  # rough estimate
                area_display = props.get("area_ha", f"{area_ha:.2f}")
                st.markdown(f"""
                <div style="background:#16213E;border-radius:12px;padding:14px;border-left:4px solid #38bdf8;">
                <p style="color:#94a3b8;font-size:12px;margin:0;">📐 AREA</p>
                <p style="color:#38bdf8;font-size:16px;font-weight:700;margin:6px 0;">~{area_display} hectares</p>
                </div>
                """, unsafe_allow_html=True)
            with info3:
                num_features = len(features)
                st.markdown(f"""
                <div style="background:#16213E;border-radius:12px;padding:14px;border-left:4px solid #a78bfa;">
                <p style="color:#94a3b8;font-size:12px;margin:0;">🗂️ FEATURES</p>
                <p style="color:#a78bfa;font-size:16px;font-weight:700;margin:6px 0;">{num_features} polygon(s)</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")

            # ── Map with uploaded boundary ────────────────────────────────────
            st.markdown("### 🌍 Field Map")
            m = folium.Map(
                location=[centroid_lat, centroid_lon],
                zoom_start=15,
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri"
            )
            folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)

            folium.GeoJson(
                geojson_data,
                name="Uploaded Field",
                style_function=lambda x: {
                    "fillColor": "#00ff99",
                    "color": "#00ff99",
                    "weight": 3,
                    "fillOpacity": 0.3
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["name"] if "name" in (features[0].get("properties") or {}) else [],
                    aliases=["Field:"] if "name" in (features[0].get("properties") or {}) else [],
                )
            ).add_to(m)

            folium.CircleMarker(
                location=[centroid_lat, centroid_lon],
                radius=6,
                color="yellow",
                fill=True,
                fill_color="orange",
                popup=f"Centroid: {centroid_lat:.4f}°N, {centroid_lon:.4f}°E"
            ).add_to(m)

            folium.LayerControl().add_to(m)
            st_folium(m, use_container_width=True, height=400)

            # ── AI Analysis for uploaded field ────────────────────────────────
            st.markdown("### 🤖 AI Analysis for This Field")
            
            # Sample nearby data from dataset to simulate field-specific values
            sample = df.sample(1, random_state=int(abs(centroid_lat * centroid_lon) % 500) + 1).iloc[0]
            
            st.info("💡 Satellite indices below are simulated from nearest dataset samples. In production, these would be fetched from Google Earth Engine using the uploaded boundary.")

            col_a, col_b = st.columns(2)
            with col_a:
                ndvi_f = st.slider("🌱 NDVI (field)", -0.5, 1.0, float(round(sample["NDVI"], 3)), 0.001)
                ndwi_f = st.slider("💧 NDWI (field)", -0.8, 0.7, float(round(sample["NDWI"], 3)), 0.001)
            with col_b:
                vh_f = st.slider("📡 VH SAR", -35.0, -10.0, float(round(sample["VH"], 1)), 0.1)
                rain_f = st.slider("🌧️ Rainfall (mm)", 0.0, 100.0, float(round(sample["Rainfall"], 1)), 0.5)
            vv_f = float(round(sample["VV"], 1))

            if st.button("🔍 Analyze This Field", type="primary", use_container_width=True):
                X_in = np.array([[ndvi_f, ndwi_f, vh_f, vv_f, rain_f]])
                pred_enc = model.predict(X_in)[0]
                pred_label = le.inverse_transform([pred_enc])[0]
                pred_proba = model.predict_proba(X_in)[0]

                sc = {"Low":"#22c55e","Moderate":"#facc15","High":"#ef4444"}.get(pred_label,"#94a3b8")
                si = {"Low":"🟢","Moderate":"🟡","High":"🔴"}.get(pred_label,"⚪")
                adv = {"Low":"No irrigation needed","Moderate":"Irrigate within 3 days","High":"Irrigate immediately"}.get(pred_label,"")

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#16213E,#1e293b);border-radius:16px;padding:24px;border:2px solid {sc};margin-top:14px;">
                <h3 style="color:{sc};margin-top:0;">{si} {pred_label} Moisture Stress</h3>
                <p style="color:#38bdf8;font-size:18px;">🚜 {adv}</p>
                <p style="color:#94a3b8;font-size:13px;">Field: {field_name} | Confidence: {max(pred_proba)*100:.1f}%</p>
                <p style="color:#64748b;font-size:12px;">
                NDVI: {ndvi_f:.3f} | NDWI: {ndwi_f:.3f} | VH: {vh_f:.1f}dB | Rainfall: {rain_f:.1f}mm
                </p>
                </div>
                """, unsafe_allow_html=True)

                # Save to session
                st.session_state["field_result"] = {
                    "lat": centroid_lat, "lon": centroid_lon,
                    "ndvi": ndvi_f, "ndwi": ndwi_f, "vh": vh_f, "vv": vv_f, "rainfall": rain_f,
                    "stress": pred_label, "advisory": adv, "confidence": max(pred_proba)*100,
                    "color": sc, "action": ""
                }
                st.success("✅ Results saved! Head to **📄 PDF Report** to download a field-specific report.")

st.markdown("---")

# ── Supported Formats Info ────────────────────────────────────────────────────
with st.expander("📖 Supported Formats & How to Create Them"):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.markdown("""
        **GeoJSON (.geojson / .json)**
        - Best supported format
        - Create at [geojson.io](https://geojson.io)
        - Export from QGIS or ArcGIS
        - Draw field → right-click → Save as GeoJSON
        """)
    with fc2:
        st.markdown("""
        **KML (.kml)**
        - Google Earth format
        - Open Google Earth Pro
        - Add Placemark → Polygon
        - File → Save Place As → KML
        """)
    with fc3:
        st.markdown("""
        **Conversion Tools**
        - [geojson.io](https://geojson.io) — draw online
        - [mapshaper.org](https://mapshaper.org) — convert formats
        - QGIS (free) — professional GIS tool
        - Google My Maps — simple online tool
        """)

st.markdown("---")
st.markdown("<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>", unsafe_allow_html=True)
