import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import plotly.express as px
from streamlit_folium import st_folium
import folium
from datetime import datetime
import numpy as np

# ================= PAGE SETTINGS =================
st.set_page_config(
    page_title="Satellite Telemetry Dashboard",
    layout="wide",
    page_icon="🛰️",
    initial_sidebar_state="expanded"
)

# ================= COLORFUL LOG FEED CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background - Light blue-gray */
    .main .block-container {
        background: linear-gradient(135deg, #f0f4f8 0%, #e3e8f0 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 0 0 25px 25px;
        margin: -1rem -1rem 3rem -1rem;
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.2);
        border: 1px solid #cbd5e1;
    }
    
    .main-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.95);
        text-align: center;
        font-size: 1.2rem;
        font-weight: 400;
        margin-top: 0.75rem;
        letter-spacing: 0.3px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.75rem;
        border-radius: 16px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-left-color: #2563eb;
    }
    
    .metric-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0;
        line-height: 1;
    }
    
    .metric-change {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1e40af;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #cbd5e1;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .status-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-normal { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    .status-warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .status-critical { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    
    /* COLORFUL LOG CONTAINER */
    .log-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 3px solid #475569;
        border-radius: 16px;
        padding: 1.5rem;
        height: 350px;
        overflow-y: auto;
        font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    
    /* Single line log entries */
    .log-entry {
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        border-radius: 10px;
        border-left: 5px solid;
        font-weight: 600;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid;
        display: flex;
        align-items: center;
        min-height: 50px;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .log-entry:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Different colorful log types */
    .log-normal { 
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left-color: #3b82f6;
        color: #1e40af;
        border-color: #93c5fd;
    }
    
    .log-warning { 
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left-color: #f59e0b;
        color: #92400e;
        border-color: #fcd34d;
    }
    
    .log-critical { 
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        border-left-color: #ef4444;
        color: #991b1b;
        border-color: #f87171;
    }
    
    .log-info { 
        background: linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%);
        border-left-color: #06b6d4;
        color: #0e7490;
        border-color: #67e8f9;
    }
    
    .log-success { 
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left-color: #10b981;
        color: #047857;
        border-color: #6ee7b7;
    }
    
    .log-system { 
        background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
        border-left-color: #a855f7;
        color: #7e22ce;
        border-color: #c084fc;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        border: 1px solid #3b82f6;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
    }
    
    /* Alert boxes with colored backgrounds */
    .stAlert {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    }
    
    /* Metric containers */
    .stMetric {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Plotly chart containers */
    .js-plotly-plot {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Map container styling */
    .folium-map {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Sidebar sections */
    .sidebar-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    /* Custom streamlit elements */
    .stTextInput input, .stNumberInput input, .stSlider {
        background: white;
        border: 1px solid #e2e8f0;
    }
    
    /* Column containers */
    .row-widget.stColumns {
        gap: 1.5rem;
    }
    
    /* Card alignment fixes */
    .element-container {
        margin-bottom: 0;
    }
    
    /* Log header styling */
    .log-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
        font-weight: 700;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2.5rem; padding: 1.5rem; background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); border-radius: 12px;'>
        <h2 style='color: white; margin-bottom: 0.5rem; font-size: 1.5rem;'>🛰️ MISSION CONTROL</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem; font-weight: 500;'>Satellite Telemetry Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2px; background: linear-gradient(90deg, #2563eb, #3b82f6); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # Configuration Section
    st.markdown("""
    <div class='sidebar-section'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>🔧 Configuration</h3>
    """, unsafe_allow_html=True)
    
    api_url = st.text_input("**API Endpoint**", "http://127.0.0.1:8000/predict", 
                          help="FastAPI endpoint for anomaly detection")
    
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("**Speed (sec)**", 0.05, 1.0, 0.15, 
                         help="Data refresh interval in seconds")
    with col2:
        limit = st.number_input("**Data Points**", 100, 2000, 500, 
                               help="Number of telemetry points to display")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Status Section
    st.markdown("""
    <div class='sidebar-section'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>📊 System Status</h3>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Last Update:** Live  
    **Connection:** Stable  
    **Data Quality:** Excellent  
    **Latency:** <50ms
    """, icon="ℹ️")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Control Buttons Section
    st.markdown("""
    <div class='sidebar-section'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>🎮 Controls</h3>
    """, unsafe_allow_html=True)
    
    control_col1, control_col2 = st.columns(2)
    with control_col1:
        if st.button("🚀 **START STREAM**", use_container_width=True, type="primary"):
            st.session_state.stream_active = True
            st.rerun()
    with control_col2:
        if st.button("⏹️ **STOP STREAM**", use_container_width=True):
            st.session_state.stream_active = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="main-header">
    <h1 class="main-title">SATELLITE TELEMETRY DASHBOARD</h1>
    <p class="main-subtitle">Advanced Real-time Monitoring & Anomaly Detection System</p>
</div>
""", unsafe_allow_html=True)

# ================= INITIALIZE SESSION STATE =================
if 'stream_active' not in st.session_state:
    st.session_state.stream_active = False
if 'anomalies' not in st.session_state:
    st.session_state.anomalies = 0
if 'packets' not in st.session_state:
    st.session_state.packets = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'current_score' not in st.session_state:
    st.session_state.current_score = 0.0
if 'current_sensors' not in st.session_state:
    st.session_state.current_sensors = {
        'battery_temp': 25.0,
        'solar_power': 180.0,
        'gyro_x': 0.0,
        'fuel_pressure': 185.0
    }

# Load sample data
@st.cache_data
def load_data():
    return pd.read_csv("data/sample_telemetry.csv", parse_dates=["timestamp"])

try:
    df = load_data()
except:
    # Create sample data if file doesn't exist
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1min')
    df = pd.DataFrame({
        'timestamp': dates,
        'battery_temp': np.random.normal(25, 8, 1000),
        'solar_power': np.random.normal(180, 25, 1000),
        'gyro_x': np.random.normal(0, 0.8, 1000),
        'fuel_pressure': np.random.normal(185, 35, 1000)
    })

# =========== ROW 1: KEY METRICS ===========
st.markdown("<div class='section-header'>📈 Mission Overview</div>", unsafe_allow_html=True)

# Equal columns with consistent spacing
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    status_color = "status-normal" if st.session_state.anomalies == 0 else "status-warning"
    status_text = "Nominal" if st.session_state.anomalies == 0 else "Monitoring"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>System Status</div>
        <div style='display: flex; align-items: center;'>
            <span class='status-indicator {status_color}'></span>
            <h2 class='metric-value'>{status_text}</h2>
        </div>
        <div class='metric-change'>All systems operational</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Total Anomalies</div>
        <h2 class='metric-value'>{st.session_state.anomalies}</h2>
        <div class='metric-change'>Last 24 hours</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Current Score</div>
        <h2 class='metric-value'>{st.session_state.current_score:.3f}</h2>
        <div class='metric-change'>Anomaly detection</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    battery_temp = st.session_state.current_sensors['battery_temp']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Battery Temp</div>
        <h2 class='metric-value'>{battery_temp:.1f}°C</h2>
        <div class='metric-change'>Within operating range</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    fuel_pressure = st.session_state.current_sensors['fuel_pressure']
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Fuel Pressure</div>
        <h2 class='metric-value'>{fuel_pressure:.1f} psi</h2>
        <div class='metric-change'>Stable</div>
    </div>
    """, unsafe_allow_html=True)

# =========== ROW 2: MAP + GAUGES ===========
st.markdown("<div class='section-header'>🌍 Satellite Tracking & Systems</div>", unsafe_allow_html=True)

# Equal columns for map and gauges
left_col, right_col = st.columns([1.4, 1])

with left_col:
    # Enhanced Map with light theme styling
    m = folium.Map(location=[25, 15], zoom_start=2, tiles="cartodbpositron")
    
    # Add satellite trajectory
    folium.PolyLine(
        [[-20, -30], [10, 0], [40, 30], [20, 60], [-10, 90]], 
        color="#2563eb", 
        weight=4, 
        opacity=0.8,
        line_cap='round'
    ).add_to(m)
    
    # Current position with enhanced marker
    folium.Marker(
        [25, 15],
        popup="<b>SAT-7B</b><br>Current Position<br>Altitude: 402km",
        tooltip="SAT-7B (Active)",
        icon=folium.Icon(color="blue", icon="satellite", prefix="fa")
    ).add_to(m)
    
    folium.CircleMarker(
        [25, 15], 
        radius=12, 
        color="#2563eb", 
        fill=True,
        fillColor="#2563eb",
        fillOpacity=0.8,
        weight=2
    ).add_to(m)
    
    st_folium(m, width=700, height=400)

with right_col:
    # Enhanced Gauges with light theme colors
    def create_gauge(title, value, min_val, max_val, color_scheme="blue"):
        if color_scheme == "blue":
            colors = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"]
        elif color_scheme == "green":
            colors = ["#059669", "#10b981", "#34d399", "#6ee7b7"]
        elif color_scheme == "orange":
            colors = ["#ea580c", "#f97316", "#fb923c", "#fdba74"]
        else:
            colors = ["#dc2626", "#ef4444", "#f87171", "#fca5a5"]
            
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title, 'font': {'size': 16, 'weight': 'bold', 'color': '#1e293b'}},
            delta={'reference': (max_val + min_val) / 2, 'font': {'size': 12, 'color': '#475569'}},
            number={'font': {'size': 22, 'weight': 'bold', 'color': '#1e293b'}},
            gauge={
                'axis': {'range': [min_val, max_val], 'tickwidth': 2, 'tickcolor': '#1e293b', 'tickfont': {'color': '#475569'}},
                'bar': {'color': colors[0], 'thickness': 0.25},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e2e8f0",
                'steps': [
                    {'range': [min_val, min_val + (max_val-min_val)*0.3], 'color': colors[3]},
                    {'range': [min_val + (max_val-min_val)*0.3, min_val + (max_val-min_val)*0.7], 'color': colors[2]},
                    {'range': [min_val + (max_val-min_val)*0.7, max_val], 'color': colors[1]}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.8,
                    'value': max_val * 0.9
                }
            }
        ))
        fig.update_layout(
            height=240, 
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor='#f8fafc',
            font={'color': "#1e293b", 'family': "Inter"},
            plot_bgcolor='#f8fafc'
        )
        return fig

    # Get current sensor values
    battery_temp = st.session_state.current_sensors['battery_temp']
    solar_power = st.session_state.current_sensors['solar_power']
    gyro_x = st.session_state.current_sensors['gyro_x']
    fuel_pressure = st.session_state.current_sensors['fuel_pressure']
    
    # Create gauges for all 4 sensors
    gauge1 = create_gauge("Battery Temp (°C)", battery_temp, -20, 60, "blue")
    gauge2 = create_gauge("Solar Power (W)", solar_power, 0, 300, "green")
    gauge3 = create_gauge("Gyro X (rad/s)", abs(gyro_x), 0, 2, "orange")
    gauge4 = create_gauge("Fuel Pressure", fuel_pressure, 50, 300, "red")
    
    # Display gauges in 2x2 grid
    gauge_col1, gauge_col2 = st.columns(2)
    with gauge_col1:
        st.plotly_chart(gauge1, use_container_width=True)
        st.plotly_chart(gauge3, use_container_width=True)
    with gauge_col2:
        st.plotly_chart(gauge2, use_container_width=True)
        st.plotly_chart(gauge4, use_container_width=True)

# =========== ROW 3: SENSOR CHARTS ===========
st.markdown("<div class='section-header'>📊 Sensor Telemetry</div>", unsafe_allow_html=True)

# Create charts for all 4 sensors
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Battery Temperature Chart
    fig_battery = px.line(
        df.tail(100), 
        x='timestamp', 
        y='battery_temp',
        title="<b>Battery Temperature Trend</b>",
        color_discrete_sequence=['#2563eb']
    )
    fig_battery.update_layout(
        height=300,
        xaxis_title="<b>Time</b>",
        yaxis_title="<b>Temperature (°C)</b>",
        template="plotly_white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        title_font_size=18,
        title_x=0.05,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#f8fafc',
    )
    fig_battery.update_traces(line=dict(width=3))
    st.plotly_chart(fig_battery, use_container_width=True)
    
    # Gyro X Chart
    fig_gyro = px.line(
        df.tail(100), 
        x='timestamp', 
        y='gyro_x',
        title="<b>Gyroscope X-Axis</b>",
        color_discrete_sequence=['#ea580c']
    )
    fig_gyro.update_layout(
        height=300,
        xaxis_title="<b>Time</b>",
        yaxis_title="<b>Angular Velocity (rad/s)</b>",
        template="plotly_white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        title_font_size=18,
        title_x=0.05,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#f8fafc',
    )
    fig_gyro.update_traces(line=dict(width=3))
    st.plotly_chart(fig_gyro, use_container_width=True)

with chart_col2:
    # Solar Power Chart
    fig_solar = px.line(
        df.tail(100), 
        x='timestamp', 
        y='solar_power',
        title="<b>Solar Power Generation</b>",
        color_discrete_sequence=['#059669']
    )
    fig_solar.update_layout(
        height=300,
        xaxis_title="<b>Time</b>",
        yaxis_title="<b>Power (W)</b>",
        template="plotly_white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        title_font_size=18,
        title_x=0.05,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#f8fafc',
    )
    fig_solar.update_traces(line=dict(width=3))
    st.plotly_chart(fig_solar, use_container_width=True)
    
    # Fuel Pressure Chart
    fig_fuel = px.line(
        df.tail(100), 
        x='timestamp', 
        y='fuel_pressure',
        title="<b>Fuel Pressure Monitoring</b>",
        color_discrete_sequence=['#dc2626']
    )
    fig_fuel.update_layout(
        height=300,
        xaxis_title="<b>Time</b>",
        yaxis_title="<b>Pressure (psi)</b>",
        template="plotly_white",
        font=dict(family="Inter", size=12, color="#1e293b"),
        title_font_size=18,
        title_x=0.05,
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#f8fafc',
    )
    fig_fuel.update_traces(line=dict(width=3))
    st.plotly_chart(fig_fuel, use_container_width=True)

# =========== ROW 4: LOGS & ALERTS ===========
st.markdown("<div class='section-header'>📡 Mission Log & Alerts</div>", unsafe_allow_html=True)

# Equal columns for logs and alerts
logs_col, alerts_col = st.columns([2, 1])

with logs_col:
    # Colorful Log Header
    st.markdown("""
    <div class='log-header'>
        📝 REAL-TIME LOG FEED
    </div>
    """, unsafe_allow_html=True)
    
    log_container = st.container()
    with log_container:
        st.markdown("<div class='log-container'>", unsafe_allow_html=True)
        # Add initial logs if empty
        if not st.session_state.logs:
            initial_logs = [
                f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 SYSTEM INITIALIZED - All systems nominal",
                f"[{datetime.now().strftime('%H:%M:%S')}] 📡 TELEMETRY STREAM STARTED - Receiving data from 4 sensors",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 SYSTEMS CHECK - All parameters within optimal range",
                f"[{datetime.now().strftime('%H:%M:%S')}] 📊 SENSORS ACTIVE - Monitoring battery_temp, solar_power, gyro_x, fuel_pressure",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🌡️ BATTERY TEMP - Current: 25.0°C | Range: -20°C to 60°C",
                f"[{datetime.now().strftime('%H:%M:%S')}] ☀️ SOLAR POWER - Current: 180.0W | Optimal generation",
                f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 GYRO X - Current: 0.000 rad/s | Stable orientation",
                f"[{datetime.now().strftime('%H:%M:%S')}] ⛽ FUEL PRESSURE - Current: 185.0 psi | Normal operation"
            ]
            for i, log in enumerate(initial_logs):
                log_class = "log-system" if i == 0 else "log-normal"
                if "BATTERY" in log:
                    log_class = "log-info"
                elif "SOLAR" in log:
                    log_class = "log-success"
                elif "GYRO" in log:
                    log_class = "log-warning"
                elif "FUEL" in log:
                    log_class = "log-critical"
                st.markdown(f"<div class='log-entry {log_class}'>{log}</div>", unsafe_allow_html=True)
        else:
            for log in st.session_state.logs[-15:]:  # Show last 15 logs
                log_class = "log-normal"
                if "ANOMALY" in log or "WARNING" in log:
                    log_class = "log-warning"
                elif "ERROR" in log or "CRITICAL" in log:
                    log_class = "log-critical"
                elif "BATTERY" in log:
                    log_class = "log-info"
                elif "SOLAR" in log:
                    log_class = "log-success"
                elif "GYRO" in log:
                    log_class = "log-warning"
                elif "FUEL" in log:
                    log_class = "log-critical"
                elif "SYSTEM" in log:
                    log_class = "log-system"
                st.markdown(f"<div class='log-entry {log_class}'>{log}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with alerts_col:
    # Alerts Section with colored background
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>🚨 Active Alerts</h3>
    """, unsafe_allow_html=True)
    
    if st.session_state.anomalies > 0:
        st.error(f"""
        **Critical Alert**
        
        **{st.session_state.anomalies}** anomalies detected
        
        **Action Required:** Review telemetry data
        """)
        
        # Sensor-specific warnings based on current values
        battery_temp = st.session_state.current_sensors['battery_temp']
        fuel_pressure = st.session_state.current_sensors['fuel_pressure']
        
        if battery_temp > 45:
            st.warning("""
            **⚠️ Battery Temp High**
            
            Temperature exceeding optimal range
            
            **Monitor:** Cooling systems
            """)
        elif fuel_pressure < 100:
            st.warning("""
            **⚠️ Fuel Pressure Low**
            
            Pressure below optimal range
            
            **Monitor:** Fuel systems
            """)
    else:
        st.success("""
        **✅ All Systems Nominal**
        
        No active alerts
        
        **Status:** Optimal performance
        **Sensors:** 4/4 operational
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sensor Status Section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 1rem;'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>📊 Sensor Status</h3>
    """, unsafe_allow_html=True)
    
    # Display current sensor values
    sensors = st.session_state.current_sensors
    st.metric("Battery Temp", f"{sensors['battery_temp']:.1f}°C")
    st.metric("Solar Power", f"{sensors['solar_power']:.1f}W")
    st.metric("Gyro X", f"{sensors['gyro_x']:.3f} rad/s")
    st.metric("Fuel Pressure", f"{sensors['fuel_pressure']:.1f} psi")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 1rem;'>
        <h3 style='color: #1e40af; margin-bottom: 1rem;'>⚡ Quick Actions</h3>
    """, unsafe_allow_html=True)
    
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with action_col2:
        if st.button("📊 Report", use_container_width=True):
            st.success("Report generated successfully!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========== STREAMING LOGIC ===========
if st.session_state.stream_active:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, row in enumerate(df.tail(limit).itertuples()):
        if not st.session_state.stream_active:
            break
            
        # Update progress
        progress = (i + 1) / limit
        progress_bar.progress(progress)
        status_text.text(f"🛰️ Processing telemetry data: {i+1}/{limit} points")
        
        # Get all 4 sensor values
        timestamp = str(row.timestamp)
        battery = row.battery_temp
        solar = row.solar_power
        gyro = row.gyro_x
        fuel = row.fuel_pressure
        
        # Update current sensor values
        st.session_state.current_sensors = {
            'battery_temp': battery,
            'solar_power': solar,
            'gyro_x': gyro,
            'fuel_pressure': fuel
        }
        
        # Send API call with all 4 sensors
        try:
            response = requests.post(api_url, json={
                "timestamp": timestamp,
                "values": {
                    "battery_temp": battery,
                    "solar_power": solar,
                    "gyro_x": gyro,
                    "fuel_pressure": fuel
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                anomaly = result.get("anomaly", False)
                score = result.get("score", 0.0)
                
                st.session_state.current_score = score
                
                if anomaly:
                    st.session_state.anomalies += 1
                    log_entry = f"[{timestamp}] ⚠️ ANOMALY DETECTED | Score: {score:.4f} | Battery: {battery:.1f}°C | Fuel: {fuel:.1f}psi"
                    st.session_state.logs.append(log_entry)
                else:
                    log_entry = f"[{timestamp}] ✅ NORMAL | Score: {score:.4f} | Solar: {solar:.1f}W | Gyro: {gyro:.3f}rad/s"
                    st.session_state.logs.append(log_entry)
                    
            else:
                log_entry = f"[{timestamp}] ❌ API ERROR | Status: {response.status_code}"
                st.session_state.logs.append(log_entry)
                
        except Exception as e:
            log_entry = f"[{timestamp}] ❌ CONNECTION ERROR | {str(e)}"
            st.session_state.logs.append(log_entry)
        
        st.session_state.packets += 1
        time.sleep(speed)
        
        # Refresh the display every 5 points for better performance
        if i % 5 == 0:
            st.rerun()
    
    progress_bar.empty()
    status_text.text("✅ Streaming completed successfully!")
    st.session_state.stream_active = False
    st.rerun()

# ================= FOOTER =================
st.markdown("""
<div style='height: 2px; background: linear-gradient(90deg, #2563eb, #3b82f6); margin: 3rem 0 1rem 0;'></div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.9rem; font-weight: 500; padding: 1rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; border: 1px solid #e2e8f0;'>"
    "Satellite Telemetry Dashboard v3.0 • Colorful Log Theme • 4-Sensor Monitoring • Last Updated: " + 
    datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
    "</div>", 
    unsafe_allow_html=True
)