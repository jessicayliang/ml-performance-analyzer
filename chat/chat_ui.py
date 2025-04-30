import streamlit as st
import requests

# ---- Configuration ----
API_URL = "http://localhost:8000/generate"

MODEL_DISPLAY_NAMES = {
    "qwen": "Qwen-0.5B",
    "llama": "Llama-1B"
}

# ---- Session State Setup ----
ss = st.session_state

if "user_id" not in ss:
    with st.form("username_form", clear_on_submit=True):
        st.title("Welcome!")
        username = st.text_input("Please enter a username to start:")
        submitted = st.form_submit_button("Start Chatting")
        if submitted:
            if username.strip() == "":
                st.warning("Username cannot be empty!")
            else:
                ss.user_id = username.strip()
                st.rerun()
    st.stop()

if "messages" not in ss:
    ss.messages = []

if "is_chat_input_disabled" not in ss:
    ss.is_chat_input_disabled = False

# ---- Sidebar ----
st.sidebar.title("Settings")
st.sidebar.markdown(f"**User ID:** `{ss.user_id}`")

model = st.sidebar.selectbox("Model", options=["llama", "qwen"], index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 0.95, 0.05)
max_tokens = st.sidebar.slider("Max Tokens", 16, 1024, 256, 16)

ss.current_model = model
display_name = MODEL_DISPLAY_NAMES.get(model, model)
st.title(f"Chat with {display_name}")

# ---- Show Messages ----
for msg in ss.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat Input ----
prompt = st.chat_input("Send a message...", disabled=ss.is_chat_input_disabled)

# ---- Handle Submission ----
if prompt or ss.is_chat_input_disabled:
    if not ss.is_chat_input_disabled and prompt:
        ss.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        ss.last_prompt = prompt  # store separately
        ss.is_chat_input_disabled = True
        st.rerun()  # to disable input and enter response block

    if ss.is_chat_input_disabled:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(API_URL, json={
                        "user_id": ss.user_id,
                        "prompt": ss.last_prompt,
                        "model": model,
                        "temperature": temperature,
                        "top_p": top_p,
                        "max_tokens": max_tokens
                    })
                    response.raise_for_status()
                    reply = response.json()["output"]
                except Exception as e:
                    reply = f"❌ Error: {e}"

                ss.messages.append({"role": "assistant", "content": reply})
                st.markdown(reply)

        ss.is_chat_input_disabled = False  # Re-enable input
        st.rerun()
