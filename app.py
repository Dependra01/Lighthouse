# app.py

import streamlit as st
from agents.query_agent import process_question

st.set_page_config(page_title="HybridOcean AI", layout="centered")

st.title("💡 HybridOcean AI")
st.markdown("Ask anything about your loyalty program data 👇")

# User input
question = st.text_area("📨 Your Question", height=100, placeholder="e.g., How many points did carpenter_228918 earn?")

if st.button("🔍 Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analysing..."):
            response = process_question(question)

        if "error" in response:
            st.error(f"❌ {response['error']}")
            if "model_reply" in response:
                st.code(response["model_reply"], language="markdown")
        else:
            st.success("✅ Query executed successfully!")
            st.markdown("### 💬 Model Reply")
            st.code(response['model_reply'], language="markdown")

            st.markdown("### 🧠 SQL Used")
            st.code(response['sql'], language="sql")

            st.markdown("### 📊 Result")
            if response["result"]:
                st.dataframe(response["result"])
            else:
                st.warning("Query ran fine but no rows were returned.")
