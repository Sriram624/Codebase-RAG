# backend/streamlit_app.py
import streamlit as st
import requests

st.set_page_config(
    page_title="Codebase RAG Assistant",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Codebase RAG Assistant")
st.caption("Local • DeepSeek + LangGraph + AST")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

BACKEND_URL = "http://localhost:8000"

def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything about your codebase..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/query",
                    json={
                        "question": prompt,
                        "chat_history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[:-1]
                        ]
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No response")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Backend error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Start it with: `docker-compose up`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Backend is taking too long.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("Status")
    if check_backend_health():
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend not running")

    st.markdown("---")
    st.markdown("**Features:**")
    st.markdown("• AST-based Code Splitting")
    st.markdown("• Intent-Aware Retrieval")
    st.markdown("• Self-Reflective Agent")
    st.markdown("• Developer-Focused Answers")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
