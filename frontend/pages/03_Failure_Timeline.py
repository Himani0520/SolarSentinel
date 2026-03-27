import streamlit as st
import pandas as pd
import plotly.express as px
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from frontend.utils.api import predict_inverter

st.set_page_config(page_title="Failure Timeline", layout="wide")
st.title("⏳ Predictive Failure Timeline")

if 'time_step' not in st.session_state:
    st.session_state.time_step = 0
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

c1, c2 = st.columns([8, 2])
with c2:
    if st.button("Stop Auto-Refresh" if st.session_state.auto_refresh else "Start Auto-Refresh"):
        st.session_state.auto_refresh = not st.session_state.auto_refresh

inverters = ["54-10-EC-8C-14-6E", "80-1F-12-0F-AC-12", "ICR2-LT1-Celestical-10000.73"]
selected_inverter = st.selectbox("Select Inverter", inverters)

with st.spinner("Fetching multi-horizon predictions..."):
    res = predict_inverter(selected_inverter, st.session_state.time_step)

if res:
    horizons = res['horizons']
    timeline_data = []
    
    # Add historical "healthy" state
    timeline_data.append({"Horizon": "0h (Now)", "Risk (%)": 0.0, "State": "Current"})
    
    for h, d in horizons.items():
        timeline_data.append({
            "Horizon": h,
            "Risk (%)": d['probability'] * 100,
            "State": "Predicted"
        })
        
    df = pd.DataFrame(timeline_data)
    
    fig = px.bar(df, x="Horizon", y="Risk (%)", color="Risk (%)",
                 color_continuous_scale=["#2ea043", "#d29922", "#f85149", "#da3633"],
                 title=f"Gradual Degradation Forecast for {selected_inverter}")
    
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    # Add a critical threshold line at 85%
    fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
    
    st.plotly_chart(fig, use_container_width=True)
    
if st.session_state.auto_refresh:
    time.sleep(5)
    st.session_state.time_step += 1
    st.rerun()
