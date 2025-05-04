# agent/query_agent.py

from llm.deepseek_chat import ask_llm
from db.connection import engine
from sqlalchemy import text

def process_question(user_question: str) -> dict:
    """
    Handles the full flow:
    - Ask Deepseek for SQL
    - Run SQL if valid
    - Return results + explanation
    """
    # Step 1: Ask LLM
    model_response = ask_llm(f"Generate only SQL to answer this: {user_question}")
    
    # Extract SQL (we assume Deepseek gives plain SQL)
    sql = extract_sql(model_response)
    if not sql:
        return {"error": "Could not extract SQL from model response.", "model_reply": model_response}
    
    # Step 2: Run the SQL
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql)).mappings().all()
            rows = [dict(row) for row in result]
    except Exception as e:
        return {"error": f"SQL execution failed: {e}", "sql": sql}

    return {
        "question": user_question,
        "sql": sql,
        "result": rows,
        "model_reply": model_response
    }

def extract_sql(response: str) -> str:
    """
    Tries to pull SQL from model's reply (removes ```sql blocks if needed)
    """
    import re
    match = re.search(r"```sql\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try fallback: raw SQL in plain text
    if "SELECT" in response.upper():
        return response.strip()
    
    return ""
