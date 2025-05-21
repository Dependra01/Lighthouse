from db.connection import engine
from sqlalchemy import text
from llm.deepseek_chat import ask_llm

def process_question(user_question: str) -> dict:
    """
    Handles the full flow:
    - Ask Deepseek for SQL
    - Run SQL if valid
    - Return results + explanation
    """
    # Step 1: Ask Deepseek
    response = ask_llm(f"Generate only SQL to answer this: {user_question}")
    model_reply = response["model_reply"]
    sql = response["sql_used"]

    if not sql or "select" not in sql.lower():
        return {
            "error": "❌ Could not extract a valid SQL query from the model response.",
            "model_reply": model_reply
        }

    # Step 2: Run SQL
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql)).mappings().all()
            rows = [dict(row) for row in result]
    except Exception as e:
        return {
            "error": f"❌ SQL execution failed: {e}",
            "sql": sql,
            "model_reply": model_reply
        }

    return {
        "question": user_question,
        "sql": sql,
        "result": rows,
        "model_reply": model_reply
    }
