# utils/sql_repairer.py

import re

def try_fix_known_sql_errors(sql: str, error_msg: str) -> str | None:
    """
    Detects common SQL issues and returns a corrected SQL version if possible.
    Returns None if no fix can be applied.
    """

    fixed_sql = sql

    # 🔧 Case 1: SUM used in WHERE clause (should be in HAVING)
    if "aggregate functions are not allowed in WHERE" in error_msg:
        where_clause_pattern = r"(WHERE\s+.*?)(AND\s+SUM\([^)]+\)\s*>[^;\n]+)"
        fixed_sql = re.sub(where_clause_pattern, r"\1", fixed_sql, flags=re.IGNORECASE)
        having_clause = re.search(r"(SUM\([^)]+\)\s*>[^;\n]+)", sql, re.IGNORECASE)
        if having_clause:
            fixed_sql = re.sub(r"(GROUP BY\s+[^\n;]+)", r"\1\nHAVING " + having_clause.group(1), fixed_sql)

    # 🔧 Case 2: Ungrouped column in SELECT
    if "must appear in the GROUP BY clause" in error_msg:
        match = re.search(r'column "(.*?)" must appear in the GROUP BY', error_msg)
        if match:
            column = match.group(1)
            # Replace column usage with STRING_AGG if it appears in SELECT
            fixed_sql = re.sub(
                fr"\b{column}\b",
                f"STRING_AGG({column}, ', ')",
                fixed_sql
            )

    # Case 3: au.phone used instead of au.mobile
    if "column \"au.phone\" does not exist" in error_msg or "au.phone" in sql:
        fixed_sql = fixed_sql.replace("au.phone", "au.mobile")


    if "operator does not exist: character varying = integer" in error_msg:
        fixed_sql = fixed_sql.replace(
            "urp.redemption_type IN (1, 2, 3)",
            "CAST(urp.redemption_type AS INT) IN (1, 2, 3)"
        )
        # 🔧 Also fix redemption_type inside CASE statements
        fixed_sql = re.sub(r"(CASE\s+WHEN\s+)(urp\.redemption_type\s*=\s*\d)",
                          r"\1CAST(\2 AS INT)",
                          fixed_sql)

    if fixed_sql != sql:
        print("\n🔧 Auto-fixed SQL (before model retry):")
        print(fixed_sql)
        return fixed_sql

    return None
