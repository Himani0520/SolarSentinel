import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from frontend.utils.api import predict_inverter

st.set_page_config(page_title="Inverter Risk Monitor", layout="wide")

st.title("⚡ Inverter Risk Monitor")

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'time_step' not in st.session_state:
    st.session_state.time_step = 0

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("Stop Auto-Refresh" if st.session_state.auto_refresh else "Start Auto-Refresh"):
        st.session_state.auto_refresh = not st.session_state.auto_refresh

inverters = ["54-10-EC-8C-14-6E", "80-1F-12-0F-AC-12", "ICR2-LT1-Celestical-10000.73"]
selected_inverter = st.selectbox("Select Inverter", inverters)

with st.spinner(f"Fetching telemetry for {selected_inverter}..."):
    res = predict_inverter(selected_inverter, st.session_state.time_step)

if not res:
    st.error("Failed to load data.")
    st.stop()
    
st.markdown("---")
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("Current Risk Score")
    score = res['max_risk_score'] * 100
    
    # Animated Gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Failure Probability (%)"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkorange"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#2ea043'},
                {'range': [30, 60], 'color': '#d29922'},
                {'range': [60, 85], 'color': '#f85149'},
                {'range': [85, 100], 'color': '#da3633'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score}
        }
    ))
    fig.update_layout(height=300, margin=dict(t=50, b=0, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"**Level:** {res['max_risk_level']}")
    st.markdown("**Top Contributors:**")
    for f in res['top_features']:
        st.markdown(f"- {f}")
        
with c2:
    st.subheader("Telemetry Trends")
    # To simulate a trend without a heavy DB, we keep a session state array
    hist_key = f"hist_{selected_inverter}"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
        
    telemetry = res['telemetry'].copy()
    
    # Inject Risk into the telemetry structure so it plots alongside the data
    telemetry['Risk (%)'] = score
    
    # keep last 20 points
    st.session_state[hist_key].append(telemetry)
    if len(st.session_state[hist_key]) > 20:
        st.session_state[hist_key].pop(0)
        
    df_hist = pd.DataFrame(st.session_state[hist_key])
    
    # Intelligently plot the exact features driving the risk, plus the Risk itself
    available_top = [f for f in res['top_features'] if f in df_hist.columns][:2]
    cols_to_plot = available_top + ['Risk (%)']
    
    # Fallback if top_features don't precisely match columns
    if len(cols_to_plot) == 1: 
        backup_cols = [c for c in df_hist.columns if c not in ['Risk (%)'] and pd.api.types.is_numeric_dtype(df_hist[c])][:2]
        cols_to_plot = backup_cols + ['Risk (%)']
        
    if cols_to_plot:
        # Scale values nicely within the 0 to 100 range for comparison with Risk
        for c in cols_to_plot:
            if c != 'Risk (%)':
                c_max = df_hist[c].max()
                if c_max > 100:
                    df_hist[c] = (df_hist[c] / c_max) * 100 # Normalize down to 100% bounds
                elif c_max <= 1.0 and c_max > 0:
                    df_hist[c] = df_hist[c] * 100 # Expand tiny normalized decimals directly to percentage scale
                
        fig2 = px.line(df_hist, y=cols_to_plot, title="Live Telemetry vs Risk Trajectory")
        
        # Lock Range to 0 - 100%
        fig2.update_yaxes(range=[0, 100])
            
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No numeric telemetry columns found to plot.")

# AI Explanation
st.markdown("---")
st.subheader("🤖 AI Operational Insight")
st.warning(res['explanation'])

if st.session_state.auto_refresh:
    time.sleep(5)
    st.session_state.time_step += 1
    st.rerun()
