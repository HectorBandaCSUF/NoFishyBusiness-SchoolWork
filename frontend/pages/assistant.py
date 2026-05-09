import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="AI Assistant", page_icon="🤖")
st.title("🤖 AI Assistant")
st.markdown("Ask any aquarium-related question and get AI-powered answers grounded in the knowledge base.")

# Initialize session state for conversation history
if "history" not in st.session_state:
    st.session_state.history = []

# Display conversation history
for msg in st.session_state.history:
    role = msg.get("role", "user")
    content = msg.get("content", "")
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.write(content)

# Chat input
user_message = st.chat_input("Ask an aquarium question...")

if user_message:
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_message)

    # Append user message to history
    st.session_state.history.append({"role": "user", "content": user_message})

    # POST to backend with last 10 history items
    with st.spinner("Loading..."):
        result = backend_post("/assistant", {
            "message": user_message,
            "history": st.session_state.history[-10:]
        })

    if result:
        reply = result.get("reply", "")
        suggested_section = result.get("suggested_section")

        # Display assistant reply
        with st.chat_message("assistant"):
            st.write(reply)
            if suggested_section:
                st.info(f"💡 Tip: Try the **{suggested_section}** for more details.")

        # Append assistant reply to history
        st.session_state.history.append({"role": "assistant", "content": reply})

        # Trim history to last 10 items (5 pairs)
        st.session_state.history = st.session_state.history[-10:]
