from db.connection import engine
from sqlalchemy import text
from llm.deepseek_chat import ask_llm, chat_with_model, extract_sql_only
from utils.sql_repairer import try_fix_known_sql_errors
import json
import streamlit as st
import decimal

MAX_RETRY_ATTEMPTS = 1

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

if 'chat_memory' not in st.session_state:
    st.session_state.chat_memory = []

def process_question(user_question: str) -> dict:
    """
    Simplified reasoning-first agent:
    - Sends user question directly to DeepSeek
    - Lets model reason freely (not limited to SQL)
    - Executes SQL if model chooses to generate it
    - Multi-turn memory is enabled, but no manual injection needed
    """
    llm_response = ask_llm(user_question)
    model_reply = llm_response["model_reply"]
    sql = llm_response["sql_used"]

    print("\n🟦 SQL from model (if any):")
    print(sql)

    if not sql or "select" not in sql.lower():
        st.session_state.chat_memory.append({
            "question": user_question,
            "sql": "No SQL generated",
            "result": [],
            "model_reply": model_reply
        })
        return {
            "question": user_question,
            "sql": "No SQL generated",
            "result": [],
            "model_reply": model_reply
        }

    for attempt in range(MAX_RETRY_ATTEMPTS + 1):
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql)).mappings().all()
                rows = [dict(row) for row in result]

            memory_entry = {
                "question": user_question,
                "sql": sql,
                "result": rows,
                "model_reply": model_reply
            }
            st.session_state.chat_memory.append(memory_entry)

            return {
                "question": user_question,
                "sql": sql,
                "result": rows,
                "model_reply": model_reply
            }

        except Exception as e:
            error_message = str(e)
            print(f"\n🟥 SQL Execution Error on attempt {attempt + 1}:")
            print(error_message)

            auto_fixed_sql = try_fix_known_sql_errors(sql, error_message)
            if auto_fixed_sql:
                sql = auto_fixed_sql
                continue

            if attempt < MAX_RETRY_ATTEMPTS:
                feedback_prompt = (
                    f"The following SQL query failed with error:\n\n{error_message}\n\n"
                    f"Original query:\n{sql}\n\nPlease correct this SQL query:"
                )
                try:
                    corrected = chat_with_model(
                        prompt=feedback_prompt,
                        system_prompt="You are an SQL expert. Correct the query based on the error message.",
                        temperature=0.2
                    )
                    sql = extract_sql_only(corrected)
                    model_reply = corrected.strip()
                    print("\n🟩 Repaired SQL from model:")
                    print(sql)
                except Exception as model_fix_error:
                    return {
                        "error": f"❌ Error during model correction: {model_fix_error}",
                        "original_error": error_message,
                        "model_reply": model_reply
                    }
            else:
                return {
                    "error": f"❌ SQL execution failed after retry: {error_message}",
                    "sql": sql,
                    "model_reply": model_reply
                }
