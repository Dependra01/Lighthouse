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
    },

    {
        "question": "How much points were redeemed in March month user-wise with name, phone, and location?",
        "sql": """
            SELECT 
                au.name AS "User Name",
                au.mobile AS "Phone Number",
                au.city AS "City",
                au.state AS "State",
                SUM(urp.points) AS "Total Points Redeemed"
            FROM 
                user_point_redemptions urp
            JOIN 
                app_users au ON au.id = urp.app_user_id
            WHERE 
                DATE(urp.created_at) >= '2025-03-01' 
                AND DATE(urp.created_at) <= '2025-03-31'
                AND urp.status != '0'
            GROUP BY 
                au.name, au.mobile, au.city, au.state
            ORDER BY 
                SUM(urp.points) DESC;
            """
    },
    {
        "question": "how many new users registered in march month give me data user type wise",
        "sql": """SELECT
                    user_type AS "User Type",
                    COUNT(*) AS "Total New Users"
                FROM
                    app_users
                WHERE
                    DATE(created_at) >= '2025-03-01' AND DATE(created_at) <= '2025-03-31'
                GROUP BY
                    user_type;
    """
    },
    {
    "question": "Who is sejal",
    "sql": "Sejal is very good girl, and she was with Deepu at UPES. She really enjoyed the environment there, especially the mountains. They worked together  in Genefied, and it went really well. Now, Sejal holds a great position in CSM and performs her work with a lot of dedication. She’s also a bit of a joker and backchod, which makes everything more fun! 😊"
    }
    # Add more as you validate them
]
