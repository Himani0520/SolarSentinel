import streamlit as st

st.set_page_config(page_title="Ask AI", layout="wide")
st.title("💬 Ask AI")

st.markdown("Query the plant infrastructure natural language model.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about high-risk inverters or maintenance schedules..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        import google.generativeai as genai
        
        # Determine current context by checking if there's any active system data in the session state
        # In this dashboard, we can just inject a general overview since the Ask AI is a standalone page
        system_context = "The system monitors 3 inverters: '54-10-EC-8C-14-6E', '80-1F-12-0F-AC-12', and 'ICR2-LT1-Celestical-10000.73'."
        
        ai_prompt = (f"System Context: {system_context}\n"
                     f"The user is asking a question about the solar inverter system. "
                     f"Please answer their question in very simple, layman terms that are easy to understand but technically accurate based on the context.\n"
                     f"User Question: {prompt}\n"
                     f"Be helpful, clear, and give easy-to-understand actionable advice.")
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            genai.configure(api_key="AIzaSyA5_93MjvXk76ZD0CeDd2COT33_SxOIhZc")
            genai_response = model.generate_content(ai_prompt)
            response = genai_response.text
        except Exception as e:
            response = f"Could not reach AI at this time. (Error: {e})"
            
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
