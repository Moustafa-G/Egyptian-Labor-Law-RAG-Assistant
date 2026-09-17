import streamlit as st

from api_client import APIError, ask_question, check_health

st.set_page_config(page_title="Egyptian Labor Law Assistant", page_icon="⚖️")

st.title("⚖️ Egyptian Labor Law Assistant")
st.caption("Ask a question about Egyptian Labor Law No. 14 of 2025 — answers are grounded in the law text with article citations.")

# --- Backend health indicator ---
health = check_health()
if health is None:
    st.error("Can't reach the backend. Make sure it's running (`uvicorn app.main:app --reload`).")
elif not health.get("vector_store_loaded"):
    st.warning("Backend is up but the vector store isn't loaded yet.")
else:
    st.success(f"Connected — {health.get('num_chunks', 0)} chunks loaded.")

st.divider()

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

# --- Chat input ---
question = st.chat_input("Ask a question about the labor law...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = ask_question(question)
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                st.markdown(answer)
                if sources:
                    st.caption("Sources: " + ", ".join(sources))
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except APIError as e:
                error_msg = f"{e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})