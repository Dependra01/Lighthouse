# utils/text_utils.py

def normalize_question(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')

    for prefix in [
        "generate only sql to answer this:",
        "write only sql to answer this:",
        "only sql to answer this:",
        "sql for:"
    ]:
        if text.startswith(prefix):
            text = text[len(prefix):]

    return text.strip()
