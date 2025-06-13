from db.connection import engine
from sqlalchemy import text
from llm.deepseek_chat import ask_llm, chat_with_model, extract_sql_blocks
from utils.sql_repairer import try_fix_known_sql_errors
from utils.smart_summarizer import summarize_result_smart
import json
import streamlit as st
import decimal
import re

MAX_RETRY_ATTEMPTS = 1

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

if 'chat_memory' not in st.session_state:
    st.session_state.chat_memory = []

def build_memory_context() -> str:
    memory = st.session_state.chat_memory[-5:]  # Use last 5 turns
    context = ""
    for turn in memory:
        context += f"User asked: {turn['question']}\n"
        context += f"Model used SQL:\n{turn['sql']}\n"
    return context

def process_question(user_question: str) -> dict:
    """
    Reasoning-first agent with automatic context injection:
    - Uses last 5 turns of memory
    - Instructs model to ask back when uncertain
    - Executes SQL only if model chooses to generate it
    """
    memory_context = build_memory_context()
    disambiguation_instruction = """
        Reasoning Rule:
            If the user's question is ambiguous or refers to a group (e.g., “carpenters”, “Delhi”, “top products”) 
            without specifying what metric or time frame they care about:
            - Do NOT assume.
            - Politely ask a clarifying question before proceeding.
            Refer to earlier questions for context, but always confirm if unclear.
    """

    enriched_prompt = f"{disambiguation_instruction}\n\n{memory_context}\nNow answer this: {user_question}"
    llm_response = ask_llm(enriched_prompt)
    print("🔍 Type of model_reply:", type(llm_response["model_reply"]))
    print("\n🧠 Full model response (raw, with <think>):")
    print(llm_response["model_reply"])
    model_reply = re.sub(r"<think>.*?</think>", "", llm_response["model_reply"], flags=re.DOTALL).strip()
    model_reply = re.sub(r"(deepseek|openai|genefied)", "HybridOcean", model_reply, flags=re.IGNORECASE)
    sql_list = extract_sql_blocks(model_reply)

    if not sql_list:
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

    print("\n🟦 SQLs from model (list):")
    for sql in sql_list:
        print(sql)

    rows = []
    for attempt in range(MAX_RETRY_ATTEMPTS + 1):
        try:
            with engine.connect() as conn:
                for sql in sql_list:
                    if not sql.strip():
                        continue
                    result = conn.execute(text(sql)).mappings().all()
                    rows.extend([dict(row) for row in result])

            clean_reply = summarize_result_smart(rows, user_question)

            memory_entry = {
                "question": user_question,
                "sql": "\n\n".join(sql_list),
                "result": rows,
                "model_reply": clean_reply
            }
            st.session_state.chat_memory.append(memory_entry)

            return memory_entry

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
                        temperature=0.2,
                        model="mistral"
                    )
                    model_reply = corrected  # keep full explanation text
                    sql_list = extract_sql_blocks(model_reply)

                    print("\n🟩 Repaired SQL(s) from model:")
                    for sql in sql_list:
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
