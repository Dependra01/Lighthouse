import streamlit as st
from agents.query_agent import process_question
# from utils.chart_renderer import render_chart_if_possible  for auto detection of graph

st.set_page_config(page_title="HybridOcean AI", layout="centered")
st.title("💡 HybridOcean AI")
st.caption("Ask anything about your loyalty program data")

# Initialize chat memory
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

# Display previous conversation turns
for turn in st.session_state.chat_memory:
    with st.chat_message("user"):
        st.markdown(turn["question"])
    with st.chat_message("assistant"):
        st.markdown(turn["model_reply"])
        if turn["result"]:
            st.dataframe(turn["result"])

# Input box for user question
user_question = st.chat_input("Type your question here...")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.spinner("Thinking..."):
        response = process_question(user_question)

    with st.chat_message("assistant"):
        if "error" in response:
            st.error(response["error"])
            if "model_reply" in response:
                st.markdown(response["model_reply"])
        else:
            st.markdown(response["model_reply"])
            if response["result"]:
                st.dataframe(response["result"])