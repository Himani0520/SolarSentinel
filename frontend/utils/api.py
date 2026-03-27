import requests
import streamlit as st

API_URL = "http://localhost:8000"

def get_health():
    try:
        res = requests.get(f"{API_URL}/health")
        return res.json()
    except Exception:
        return {"status": "offline"}

def predict_inverter(inverter_id, time_step=0):
    try:
        res = requests.post(f"{API_URL}/predict", json={"inverter_id": inverter_id, "time_step": time_step})
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"API Error: {res.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}. Is the backend running?")
        return None
