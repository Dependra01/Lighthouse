from db.connection import engine
from sqlalchemy import text
from utils.sql_repairer import try_fix_known_sql_errors
from llm.deepseek_chat import ask_llm, chat_with_model
from rag.schema_retriever import retrieve_schema_chunks
from llm.deepseek_chat import SCHEMA_PRIMER, SYSTEM_PROMPT
import json

MAX_RETRY_ATTEMPTS = 1

def process_question(user_question: str) -> dict:
    # Initial SQL generation
    llm_response = ask_llm(f"Generate only SQL to answer this: {user_question}")
    model_reply = llm_response["model_reply"]
    sql = llm_response["sql_used"]

    print("\n🟦 Original SQL from model:")
    print(sql)


    if not sql or "select" not in sql.lower():
        return {
            "error": "❌ Could not extract a valid SQL query from the model response.",
            "model_reply": model_reply
        }

    # SQL execution and retry logic
    for attempt in range(MAX_RETRY_ATTEMPTS + 1):
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql)).mappings().all()
                rows = [dict(row) for row in result]
            print("✅ SQL executed successfully.\n")
            # Successful execution
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

            # 🔁 Auto-repair before LLM
            auto_fixed_sql = try_fix_known_sql_errors(sql, error_message)
            if auto_fixed_sql:
                sql = auto_fixed_sql
                continue

            if attempt < MAX_RETRY_ATTEMPTS:
                print("\n🛠️ Sending error back to model for correction...")
                # Feedback loop for correction
                feedback_prompt = (
                    f"The following SQL query has failed with the error:\n\n"
                    f"{error_message}\n\n"
                    f"Original query:\n{sql}\n\n"
                    f"Please correct this SQL query:"
                )
                try:
                    schema_context = "\n\n".join(retrieve_schema_chunks(user_question))

                    corrected_response = chat_with_model(
                        prompt=feedback_prompt,
                        system_prompt=SCHEMA_PRIMER + "\n\n" + SYSTEM_PROMPT + "\n\n" + schema_context,
                        temperature=0.1
                    )
                    sql = extract_sql_only(corrected_response)
                    model_reply = corrected_response.strip()
                    print("\n🟩 Repaired SQL from model:")
                    print(sql)
                except Exception as feedback_error:
                    print("❌ Model failed during error correction.")
                    return {
                        "error": f"❌ Error during model correction: {feedback_error}",
                        "original_error": error_message,
                        "model_reply": corrected_response if 'corrected_response' in locals() else ""
                    }
            else:
                print("❌ Model failed during all error correction.")
                # After max retries, return the error
                return {
                    "error": f"❌ SQL execution failed after retry: {error_message}",
                    "sql": sql,
                    "model_reply": model_reply
                }

# Helper function to extract SQL cleanly
def extract_sql_only(response: str) -> str:
    import re
    match = re.search(r"```sql\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"(SELECT|WITH)\s.*", response, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(0).strip()

    return response.strip()