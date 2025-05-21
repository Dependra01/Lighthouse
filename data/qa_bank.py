canonical_qa_bank = [
    {
        "question": "How many distinct user types do we have in the system?",
        "sql": "SELECT COUNT(DISTINCT user_type) AS \"Total\" FROM app_users;"
    },
    {
        "question": "How many dealers are in each city?",
        "sql": "SELECT \n    au.city as \"City\",\n    COUNT(*) AS \"Dealers Count\"\nFROM \n    app_users au\nWHERE \n    au.user_type LIKE '%dealer%'\n    AND au.city IS NOT NULL\nGROUP BY \n    au.city\nORDER BY \n    \"Dealers Count\" DESC;"
    },
    {
        "question": "What are the top 3 most scanned products?",
        "sql": "SELECT product_code, COUNT(*) AS scan_count FROM user_point_entries WHERE status = '1' AND is_reverted = FALSE GROUP BY product_code ORDER BY scan_count DESC LIMIT 3;"
    },
    {
        "question": "How many total points have been redeemed?",
        "sql": "SELECT SUM(points) AS total_redeemed FROM user_point_redemptions WHERE status != '0';"
    },
    {
    "question": "give dealer distribution by city\"",
    "sql": "SELECT DISTINCT \n    city AS \"City\",\n    COUNT(*) AS \"Dealer Count\"\nFROM app_users\nWHERE user_type = 'dealer'\n    AND city IS NOT NULL\nGROUP BY city\nORDER BY \"Dealer Count\" DESC;"
    },
    {
    "question": "how many dealer i have",
    "sql": "SELECT COUNT(*) AS \"Total Dealers\"\nFROM app_users\nWHERE user_type LIKE '%dealer%';"
    },
    {
        "question": "how many total dealers in my loyalty program",
        "sql": "SELECT COUNT(*) AS \"Total Dealers\"\nFROM app_users\nWHERE user_type LIKE '%dealer%';"
    },
    {
        "question": "how many total dealers in my loyalty program",
        "sql": "SELECT COUNT(*) AS \"Total Dealers\"\nFROM app_users\nWHERE user_type LIKE '%dealer%';"
    }

    # Add more as you validate them
]
