from db.connection import engine
from sqlalchemy import text
from llm.deepseek_chat import ask_llm, chat_with_model, extract_sql_only
from utils.sql_repairer import try_fix_known_sql_errors
import json
import streamlit as st
import decimal
import re

MAX_RETRY_ATTEMPTS = 1

# Support Decimal encoding for JSON dumps
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

# Initialize Streamlit session state for chat memory
if 'chat_memory' not in st.session_state:
    st.session_state.chat_memory = []

def process_question(user_question: str) -> dict:
    """
    Handles multi-turn memory-based chat:
    - Injects previous Q + SQL + result + table context
    - Runs SQL with retry and repair
    - Stores memory in session
    """
    chat_memory = st.session_state.chat_memory
    previous = chat_memory[-1] if chat_memory else None

    memory_context = ""
    if previous:
        # Extract involved table names from previous SQL
        tables = re.findall(r'from\s+(\w+)|join\s+(\w+)', previous['sql'], re.IGNORECASE)
        flat_tables = [t for pair in tables for t in pair if t]
        table_note = (
            f"The previous SQL queried the following tables: {', '.join(set(flat_tables))}.\n"
            f"You may refer to these tables again if the user's new question is related to them.\n"
        )

        memory_context = f"""
Previous Question: {previous['question']}

Previous SQL:
{previous['sql']}

Previous Result:
{json.dumps(previous['result'], indent=2, cls=DecimalEncoder)}

{table_note}
If the new question is unrelated, feel free to ignore previous context.
        """

    enriched_prompt = f"{memory_context}\nNow answer this fresh user question: {user_question}"
    llm_response = ask_llm(enriched_prompt)
    model_reply = llm_response["model_reply"]
    sql = llm_response["sql_used"]

    print("\n🟦 SQL from model:")
    print(sql)

    if not sql or "select" not in sql.lower():
        return {
            "error": "❌ Could not extract a valid SQL query from the model response.",
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
                "result": rows
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
