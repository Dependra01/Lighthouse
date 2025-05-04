few_shot_examples = [
    {
        "question": "How many distinct user types do we have in the system?",
        "query": """
            SELECT COUNT(DISTINCT user_type) AS "Total" FROM app_users;
        """
    },
    {
        "question": "Could you provide a breakdown of user count by each user type?",
        "query": """
            SELECT user_type AS "User Type", COUNT(*) AS "Total" 
            FROM app_users 
            GROUP BY user_type;
        """
    },
    {
        "question": "Which fabricator recorded the highest number of scans in February?",
        "query": """
            SELECT au.name as "Name", au.mobile as "Mobile", COUNT(1) as "Total Scan"
            FROM user_point_entries upe
            LEFT JOIN app_users au ON au.id = upe.app_user_id 
            WHERE DATE(upe.created_at) >= '2025-02-01' AND DATE(upe.created_at) <= '2025-02-28'
            GROUP BY upe.app_user_id, au.name, au.mobile
            ORDER BY COUNT(1) DESC
            LIMIT 1;
        """
    },
    {
        "question": "Can you share the total number of scans performed in each city?",
        "query": """
            SELECT au.city as "City", COUNT(1) as "Total Scan"
            FROM user_point_entries upe
            LEFT JOIN app_users au ON au.id = upe.app_user_id
            WHERE upe.status = '1' AND upe.is_reverted = FALSE
            GROUP BY au.city;
        """
    },
    {
        "question": "What are the top 3 most scanned products across the platform?",
        "query": """
            SELECT product_code as "Product Code", COUNT(1) as "Count"
            FROM user_point_entries upe 
            WHERE status = '1' AND is_reverted = FALSE 
            GROUP BY product_code 
            ORDER BY COUNT(1) DESC 
            LIMIT 3;
        """
    },
    {
        "question": "What’s the total number of users who registered over the past six months?",
        "query": """
            SELECT 
                TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
                COUNT(*) AS "user count"
            FROM app_users
            WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY month
            ORDER BY month;
        """
    },
    {
        "question": "How many new users registered during the month of February?",
        "query": """
            SELECT COUNT(*) as "Total"
            FROM app_users 
            WHERE DATE(created_at) >= '2025-02-01' AND DATE(created_at) <= '2025-02-28';
        """
    },
    {
        "question": "How many dealers are in each city?",
        "query": """
            SELECT 
                city AS "City", 
                COUNT(*) AS "Total Dealer"
            FROM app_users
            WHERE 
                user_type LIKE '%dealer%' 
                AND city IS NOT NULL
            GROUP BY city;
        """
    }
]