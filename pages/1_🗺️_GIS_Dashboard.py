import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, MiniMap, MousePosition
import streamlit as st

st.set_page_config(
    page_title="GIS Dashboard – AgriAstra",
    page_icon="🗺️",
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

# ── Status Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="
background:linear-gradient(90deg,#14532d,#166534);
padding:15px;
border-radius:12px;
margin-bottom:15px;
color:white;
box-shadow:0 4px 10px rgba(0,0,0,0.3);
">
<h3 style="margin-top:0; color:white;">🛰️ GIS Dashboard Status</h3>

<table style="width:100%;font-size:16px;color:white;border-collapse:collapse;">
<tr>
<td>🟢 <b>Satellite Layer</b></td><td>Loaded</td>
<td>🤖 <b>AI Model</b></td><td>Random Forest</td>
</tr>
<tr>
<td>🗺️ <b>District Boundary</b></td><td>Loaded</td>
<td>📍 <b>Study Area</b></td><td>Nalgonda</td>
</tr>
<tr>
<td>🌧️ <b>Rainfall Data</b></td><td>Available</td>
<td>📅 <b>Status</b></td><td>Online</td>
</tr>
</table>
</div>
""", unsafe_allow_html=True)

# ── Interactive Map ────────────────────────────────────────────────────────────
st.subheader("🌍 Interactive GIS Map")

m = folium.Map(
    location=[17.0575, 79.2671],
    zoom_start=10,
    tiles=None,
    control_scale=True
)

Fullscreen(
    position="topright",
    title="Full Screen",
    title_cancel="Exit Full Screen",
    force_separate_button=True
).add_to(m)

MiniMap(toggle_display=True).add_to(m)
MousePosition().add_to(m)

folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
folium.TileLayer("CartoDB Positron", name="Light Map").add_to(m)
folium.TileLayer("CartoDB Dark_Matter", name="Dark Map").add_to(m)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Satellite",
    overlay=False,
    control=True
).add_to(m)

folium.GeoJson(
    "geojson/nalgonda.geojson",
    name="Nalgonda Boundary",
    style_function=lambda feature: {
        "fillColor": "#00FF66",
        "color": "#00FF66",
        "weight": 2,
        "fillOpacity": 0.12
    },
    highlight_function=lambda feature: {
        "fillColor": "#00FF66",
        "color": "#FFFF00",
        "weight": 5,
        "fillOpacity": 0.30
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["shapeName"],
        aliases=["District:"],
        sticky=True
    )
).add_to(m)

m.fit_bounds([[16.65, 78.70], [17.55, 79.75]])

folium.CircleMarker(
    location=[17.0575, 79.2671],
    radius=8,
    color="yellow",
    fill=True,
    fill_color="red",
    fill_opacity=1,
    popup="Study Area - Nalgonda"
).add_to(m)

folium.LayerControl().add_to(m)

legend_html = """
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 220px;
background-color: rgba(15,23,42,0.92);
border:2px solid #00ff66;
border-radius:10px;
padding:12px;
font-size:14px;
color:white;
z-index:9999;
box-shadow:0 4px 12px rgba(0,0,0,0.5);
">
<h4 style="margin-top:0;color:#00ff66;">🗺️ Legend</h4>
<p>🟢 <b>Low Stress</b></p>
<p>🟡 <b>Moderate Stress</b></p>
<p>🔴 <b>High Stress</b></p>
<hr>
<p>🟩 <b>Nalgonda Boundary</b></p>
<p>📍 <b>Study Area</b></p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, use_container_width=True, height=500)

st.markdown("---")

# ── Static GIS Images ──────────────────────────────────────────────────────────
st.subheader("🛰️ GIS Visualization")

m1, m2, m3 = st.columns(3)

with m1:
    st.image(
        "dashboard/assets/ndvi_map.jpeg",
        caption="🌱 NDVI Map",
        use_container_width=True
    )

with m2:
    st.image(
        "dashboard/assets/moisture_stress_map.jpeg",
        caption="💧 Moisture Stress Map",
        use_container_width=True
    )

with m3:
    st.image(
        "dashboard/assets/irrigation_map.jpeg",
        caption="🚜 Irrigation Advisory Map",
        use_container_width=True
    )

st.markdown("---")
st.markdown(
    "<center><h4>🌾 AgriAstra | Precision Agriculture using AI + GIS</h4></center>",
    unsafe_allow_html=True
)
