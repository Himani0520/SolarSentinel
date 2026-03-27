import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from frontend.utils.api import predict_inverter

st.set_page_config(page_title="Overview", layout="wide")

st.title("🌐 Plant Overview")

# Initialize auto-refresh state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'time_step' not in st.session_state:
    st.session_state.time_step = 0

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("Stop Auto-Refresh" if st.session_state.auto_refresh else "Start Auto-Refresh"):
        st.session_state.auto_refresh = not st.session_state.auto_refresh

# Fetch data for all inverters
inverters = ["54-10-EC-8C-14-6E", "80-1F-12-0F-AC-12", "ICR2-LT1-Celestical-10000.73"]
data = []

with st.spinner(f"Fetching live telemetry (T={st.session_state.time_step})..."):
    for inv in inverters:
        res = predict_inverter(inv, st.session_state.time_step)
        if res:
            data.append(res)
            
if not data:
    st.warning("Waiting for API Backend...")
    st.stop()
    
# Process KPIs
risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
total_score = 0
for d in data:
    risk_counts[d['max_risk_level']] += 1
    total_score += d['max_risk_score']
    
avg_score = total_score / len(data)

# KPI Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Inverters", len(data))
kpi2.metric("Critical Risk", risk_counts["CRITICAL"])
kpi3.metric("High Risk", risk_counts["HIGH"])
kpi4.metric("Medium Risk", risk_counts["MEDIUM"])
kpi5.metric("Avg Risk Score", f"{avg_score*100:.1f}%")

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Risk Distribution")
    # Donut chart
    labels = list(risk_counts.keys())
    values = list(risk_counts.values())
    colors = ['#2ea043', '#d29922', '#f85149', '#da3633'] # Custom UI Colors
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors))])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    
with col2:
    st.markdown("### Inverter Status Matrix")
    # Table
    table_data = []
    for d in data:
        table_data.append({
            "Inverter ID": d['inverter_id'],
            "Risk Score": f"{d['max_risk_score']*100:.1f}%",
            "Risk Level": d['max_risk_level'],
            "Status": "Online",
            "Timestep": d['time_step_used']
        })
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

if st.session_state.auto_refresh:
    time.sleep(5)
    st.session_state.time_step += 1
    st.rerun()
