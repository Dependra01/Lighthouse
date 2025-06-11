import streamlit as st
from agents.query_agent import process_question

st.set_page_config(page_title="HybridOcean AI", layout="centered")

st.title("💡 HybridOcean AI")
st.caption("Ask anything about your loyalty program data")

# --- Init memory ---
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

# --- Display past conversation ---
with st.container():
    for entry in st.session_state.chat_memory:
        with st.chat_message("user"):
            st.markdown(entry["question"])
        with st.chat_message("assistant"):
            st.markdown("**SQL**")
            st.code(entry["sql"], language="sql")
            st.markdown("**Result**")
            st.dataframe(entry["result"])

# --- New chat input ---
user_question = st.chat_input("Ask your next question...")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.spinner("💭 Thinking..."):
        response = process_question(user_question)

    with st.chat_message("assistant"):
        if "error" in response:
            st.error(response["error"])
            if "model_reply" in response:
                st.code(response["model_reply"], language="markdown")
        else:
            st.success("✅ Query executed successfully!")
            st.markdown("**SQL**")
            st.code(response["sql"], language="sql")
            st.markdown("**Result**")
            st.dataframe(response["result"])