import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Visualize", layout="wide")
st.title("📊 Visualize Your Data")

# 🔁 Load last result from memory
if "chat_memory" in st.session_state and st.session_state.chat_memory:
    last_result = st.session_state.chat_memory[-1].get("result", [])
    if last_result:
        df = pd.DataFrame(last_result)

        st.success("✅ Data loaded from your last question.")

        # 👁 Show raw table (collapsible)
        with st.expander("🔍 View Data Table", expanded=False):
            st.dataframe(df)

        # 📌 Column selection
        st.subheader("🎯 Customize Your Chart")
        x_axis = st.selectbox("Choose X-axis", df.columns)
        y_axis = st.selectbox("Choose Y-axis", df.columns)
        chart_type = st.selectbox("Choose Chart Type", ["Bar", "Line", "Pie"])

        # 📊 Chart rendering
        fig = None
        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, text=y_axis)
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, markers=True)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_axis, values=y_axis)

        fig.update_layout(
            title= "HybridOcean AI",
            plot_bgcolor="Black",
            paper_bgcolor="Black",
            xaxis_title=x_axis.title(),
            yaxis_title=y_axis.title(),
        )

        st.plotly_chart(fig, use_container_width=True)

        # 💾 Optionally export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "data.csv", "text/csv")
    else:
        st.warning("No data available from previous chat. Ask a question first.")
else:
    st.info("Please ask a question in the main chat to generate data for visualization.")
