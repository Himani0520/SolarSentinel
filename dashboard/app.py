import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="Inverter Intelligence Platform", layout="wide")

st.markdown("## ☀️ Aubergine AI Inverter Dashboard")
st.markdown("Predictive maintenance and generative AI insights for solar infrastructure.")

# Real Inverters Based on the 3 Datasets
inverters = ["54-10-EC-8C-14-6E", "80-1F-12-0F-AC-12", "ICR2-LT1-Celestical-10000.73"]

selected_inverter = st.sidebar.selectbox("Select Inverter", inverters)

# Add time slider
st.sidebar.markdown("### ⏳ Time Machine")
st.sidebar.caption("Simulate time advancing towards the end of the telemetry dataset. 0 is early, 3000 is late.")
time_step = st.sidebar.slider("Simulation Step (5-min intervals)", min_value=0, max_value=3000, value=3000, step=100)

st.write(f"### Results for {selected_inverter}")
col1, col2 = st.columns([1.5, 1])

try:
    response = requests.post("http://127.0.0.1:8000/predict", json={"inverter_id": selected_inverter, "time_step": time_step})
    if response.status_code == 200:
        data = response.json()
        results = data["horizons"]
        max_risk_level = data["max_risk_level"]
        max_prob = data["max_risk_score"]
        
        with col1:
            st.subheader("Gradual Multi-Horizon Risk Assessment")
            st.markdown("#### Degradation Forecast Timeline")
            color_map = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🟠",
                "CRITICAL": "🔴"
            }
            for h, h_data in results.items():
                risk_lvl = h_data['risk_level']
                prob = h_data['probability'] * 100
                st.markdown(f"**{h} Risk**: {color_map[risk_lvl]} {risk_lvl} ({prob:.1f}%)")
                
        with col2:
            st.subheader("GenAI Operator Summary")
            
            if max_risk_level == "LOW":
                res = f"Inverter '{selected_inverter}' is operating efficiently with negligible risk ({max_prob*100:.1f}%) of near-term failure. No operational intervention is required."
            elif max_risk_level in ["MEDIUM", "HIGH"]:
                res = (f"The Multi-Horizon prediction engine detects a degrading trend for inverter '{selected_inverter}'. "
                       f"The system indicates a {max_risk_level} risk ({max_prob*100:.1f}%) of failure materializing over the coming days. "
                       f"**RECOMMENDED ACTION**: Schedule preventative maintenance and inspect environmental factors near the unit.")
            else:
                res = (f"🚨 **CRITICAL ALARM**: The ML model predicts an imminent {max_prob*100:.1f}% probability of total failure for inverter '{selected_inverter}'. "
                       f"The localized multi-horizon sequence indicates rapid degradation. "
                       f"**RECOMMENDED ACTION**: Dispatch field operatives immediately to isolate the string and perform a localized IV curve trace on affected panel chains.")
            
            st.info(res)
            
            # Display real Gemini summary from backend if it generated one
            explanation = data.get('explanation', '')
            if explanation and "Failed to generate" not in explanation:
                st.markdown("### AI Details")
                st.markdown(explanation)
                
    else:
        st.error(f"Backend API error: {response.text}")

except Exception as e:
    st.error(f"Could not connect to backend API: {e}. Please ensure it is running at http://127.0.0.1:8000")

st.markdown("---")
st.markdown("### Historical Power Generation Trend")
st.markdown("*(Simulated historical correlation view)*")
# Using the exact images we saved during EDA
image_path = f"eda_outputs/Copy of {selected_inverter}.raws.csv_power_trend.png"
if os.path.exists(image_path):
    st.image(image_path)
else:
    st.write("Historical image plot currently unavailable.")
