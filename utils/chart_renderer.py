# import pandas as pd
# import streamlit as st
# import plotly.express as px

# def render_chart_if_possible(rows: list[dict]):
#     if not rows:
#         return

#     df = pd.DataFrame(rows)
#     if df.empty or df.shape[1] < 2:
#         return

#     df.columns = df.columns.str.lower()
#     columns = df.columns.tolist()

#     first_col = columns[0]
#     second_col = columns[1]

#     # Try to convert second column to numeric if it's not
#     df[second_col] = pd.to_numeric(df[second_col], errors='coerce')

#     first_is_categorical = df[first_col].dtype == object or df[first_col].nunique() < 15
#     second_is_numeric = pd.api.types.is_numeric_dtype(df[second_col])

#     if any(k in first_col for k in ["month", "date", "year"]):
#         st.markdown("📈 **Trend Over Time:**")
#         fig = px.line(df.sort_values(first_col), x=first_col, y=second_col, markers=True)
#         fig.update_layout(title=None, xaxis_title=first_col.title(), yaxis_title=second_col.title())
#         st.plotly_chart(fig, use_container_width=True)
#         return

#     if first_is_categorical and second_is_numeric:
#         st.markdown("📊 **Category Breakdown:**")
#         fig = px.bar(df, x=first_col, y=second_col, text=second_col)
#         fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
#         fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#         fig.update_layout(title=None, xaxis_title=first_col.title(), yaxis_title=second_col.title())
#         st.plotly_chart(fig, use_container_width=True)
#         return

#     if df.shape[0] <= 20 and second_is_numeric:
#         st.markdown("📊 **Top Entities Chart:**")
#         fig = px.bar(df, x=first_col, y=second_col, text=second_col)
#         st.plotly_chart(fig, use_container_width=True)
