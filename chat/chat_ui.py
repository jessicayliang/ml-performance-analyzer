import streamlit as st
import requests

# ---- Configuration ----
API_URL = "http://localhost:8000/generate"

# Map model short names to pretty names
MODEL_DISPLAY_NAMES = {
    "qwen": "Qwen-0.5B",
    "llama": "Llama-1B"
}

# ---- User ID Setup ----
if "user_id" not in st.session_state:
    with st.form("username_form", clear_on_submit=True):
        st.title("Welcome!")
        username = st.text_input("Please enter a username to start:")
        submitted = st.form_submit_button("Start Chatting")

        if submitted:
            if username.strip() == "":
                st.warning("Username cannot be empty!")
            else:
                st.session_state.user_id = username.strip()
                st.rerun()

    st.stop()

# ---- Sidebar controls ----
st.sidebar.title("Settings")
st.sidebar.markdown(f"**User ID:** `{st.session_state.user_id}`")  # Display non-editable

model = st.sidebar.selectbox("Model", options=["llama", "qwen"], index=0)
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
top_p = st.sidebar.slider("Top-p", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
max_tokens = st.sidebar.slider("Max Tokens", min_value=16, max_value=1024, value=256, step=16)

# ---- Chat History ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# (IMPORTANT) Don't reset messages when model switches
st.session_state.current_model = model  # update selected model

# ---- Page title ----
display_name = MODEL_DISPLAY_NAMES.get(model, model)
st.title(f"Chat with {display_name}")

# ---- Display message history ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- User Input ----
if prompt := st.chat_input("Send a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add loading spinner while waiting for model
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={
                    "user_id": st.session_state.user_id,
                    "prompt": prompt,
                    "model": model,  # send the selected model
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens
                })
                response.raise_for_status()
                reply = response.json()["output"]
            except Exception as e:
                reply = f"❌ Error: {e}"

            # Add assistant reply
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.markdown(reply)
