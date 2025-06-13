from utils.result_summarizer import summarize_sql_result
from llm.deepseek_chat import chat_with_model


def summarize_result_smart(rows: list[dict], question: str, fallback_model="mistral") -> str:
    """
    First try fast rule-based summary.
    If not clear or too vague, fallback to Mistral or Phi-3 for LLM summarization.
    """
    fast_summary = summarize_sql_result(rows, question)

    if "found" in fast_summary.lower() or "breakdown" in fast_summary.lower():
        try:
            formatted = "\n".join([str(row) for row in rows[:5]])
            llm_summary = chat_with_model(
                prompt=f"The user asked: {question}\n\nHere is the SQL result:\n{formatted}\n\nSummarize this in a natural way.",
                system_prompt="You are a helpful assistant. Respond with a clean natural summary.",
                model=fallback_model,
                temperature=0.4
            )
            return llm_summary.strip()
        except Exception:
            return fast_summary

    return fast_summary
