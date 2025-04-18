import streamlit as st
import requests

# ---- Configuration ----
API_URL = "http://localhost:8000/generate"

# ---- Sidebar controls ----
st.sidebar.title("Settings")
user_id = st.sidebar.text_input("User ID", value="user-101")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
top_p = st.sidebar.slider("Top-p", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
max_tokens = st.sidebar.slider("Max Tokens", min_value=16, max_value=1024, value=256, step=16)

# ---- Chat History ----
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chat with Qwen-0.5B")

# ---- Display message history ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- User Input ----
if prompt := st.chat_input("Send a message..."):
    # Add user message to local history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send API request
    try:
        response = requests.post(API_URL, json={
            "user_id": user_id,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        })
        response.raise_for_status()
        reply = response.json()["output"]
    except Exception as e:
        reply = f"❌ Error: {e}"

    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
