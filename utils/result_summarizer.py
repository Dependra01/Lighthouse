def summarize_sql_result(rows: list[dict], question: str) -> str:
    """
    Rule-based fast summary generator for SQL result.
    Returns a clean, natural one-liner.
    """
    if not rows:
        return "No data found for your request."

    # Case: Single value count
    if len(rows) == 1 and len(rows[0]) == 1:
        key = list(rows[0].keys())[0]
        val = rows[0][key]
        return f"The result is: **{val}**."

    # Case: Two values in one row (e.g., Feb vs March)
    if len(rows) == 1 and len(rows[0]) == 2:
        keys = list(rows[0].keys())
        a, b = rows[0][keys[0]], rows[0][keys[1]]
        try:
            diff = b - a
            pct = (diff / a) * 100 if a else 0
            trend = "increase" if diff > 0 else "decrease" if diff < 0 else "no change"
            return (
                f"In comparison: **{keys[0]}** had {a}, **{keys[1]}** had {b}. "
                f"That’s a {trend} of **{abs(diff)}** ({abs(pct):.1f}%)."
            )
        except Exception:
            return f"{keys[0]}: {a}, {keys[1]}: {b}"

    # Case: 1 row with categories (e.g., user type, month)
    if len(rows) == 1:
        parts = [f"**{k}**: {v}" for k, v in rows[0].items()]
        return "Here’s what I found: " + ", ".join(parts)

    # Case: multi-row with month/user_type breakdown
    if any("month" in k.lower() for k in rows[0]) and "count" in str(rows[0].keys()).lower():
        return "Here’s a monthly breakdown of your data."

    if any("user_type" in k.lower() for k in rows[0]):
        return "Here’s how the results look by user type."

    return f"I found **{len(rows)} rows** based on your query."
