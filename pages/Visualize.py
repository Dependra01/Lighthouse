import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Visualize", layout="wide")
st.title("📊 Visualize Your Data")

# Load all past results
chat_memory = st.session_state.get("chat_memory", [])

# Filter only those with results
visualizable = [entry for entry in chat_memory if entry.get("result")]

if not visualizable:
    st.warning("No data available from previous chat. Ask a question first.")
    st.stop()

# Select from past questions
options = [f"{i+1}. {entry['question'][:80]}" for i, entry in enumerate(visualizable)]
selected_index = st.selectbox("Select a past question to visualize", options)
selected_entry = visualizable[int(selected_index.split(".")[0]) - 1]
df = pd.DataFrame(selected_entry["result"])

st.success(f"✅ Showing result for: *{selected_entry['question']}*")

# 👁 Show raw table
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
    title="HybridOcean AI",
    plot_bgcolor="Black",
    paper_bgcolor="Black",
    xaxis_title=x_axis.title(),
    yaxis_title=y_axis.title(),
)

st.plotly_chart(fig, use_container_width=True)

# 💾 CSV Export
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, "data.csv", "text/csv")
