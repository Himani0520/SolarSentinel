import streamlit as st
import os

st.set_page_config(
    page_title="Solar Intelligence Platform",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme and CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
    }
    .css-1d391kg {
        background-color: #161b22;
    }
    h1, h2, h3 {
        color: #e6edf3;
    }
    .metric-card {
        background-color: #21262d;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #30363d;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff7b00; /* Solar Orange */
    }
</style>
""", unsafe_allow_html=True)

# Initialize global time state
if 'time_step' not in st.session_state:
    st.session_state.time_step = 0

st.title("☀️ Aubergine AI Inverter Intelligence")
st.markdown("### Next-Generation Infrastructure Monitoring")

st.markdown("""
Welcome to the Solar Inverter Intelligence Platform. 

Please navigate using the sidebar to explore the multi-horizon risk predictions, AI insights, and live infrastructure graphs.

**Dataset Status:** 
The backend connects securely to three major solar plant datasets. Inference is continuously streamed using rolling-window prediction models.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><h3>Active Plants</h3><div class="metric-value">3</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3>Monitored Inverters</h3><div class="metric-value">3</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h3>Multi-Horizon Scope</h3><div class="metric-value">10 Levels</div></div>', unsafe_allow_html=True)
