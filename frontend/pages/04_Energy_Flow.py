import streamlit as st
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Energy Flow", layout="wide")
st.title("⚡ Energy Flow Visualization")

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'time_step' not in st.session_state:
    st.session_state.time_step = 0
c1, c2 = st.columns([8, 2])
with c2:
    if st.button("Stop Auto-Refresh" if st.session_state.auto_refresh else "Start Auto-Refresh"):
        st.session_state.auto_refresh = not st.session_state.auto_refresh

st.markdown("Dynamic visualization of DC to AC conversions across the solar plant.")

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["Solar Array Alpha", "Solar Array Beta", "Inverter 54-10-EC", "Inverter 80-1F-12", "Inverter ICR2", "Plant Grid Export"],
      color = ["orange", "orange", "blue", "blue", "blue", "green"]
    ),
    link = dict(
      source = [0, 0, 1, 1, 2, 3, 4], # indices correspond to labels
      target = [2, 3, 3, 4, 5, 5, 5],
      value = [100, 50, 80, 120, 140, 120, 110]
  ))])

fig.update_layout(title_text="Real-time DC/AC Flow", font_size=12, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=500)
st.plotly_chart(fig, use_container_width=True)

if st.session_state.auto_refresh:
    time.sleep(5)
    st.session_state.time_step += 1
    st.rerun()
