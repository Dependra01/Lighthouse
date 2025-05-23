# db/queries.py

from sqlalchemy import text
from db.connection import engine

# def get_user_by_mobile(mobile_number):
#     query = text("""
#         SELECT * FROM app_users
#         WHERE mobile = :mobile
#         LIMIT 1
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {"mobile": mobile_number}).mappings().fetchone()
#         return dict(result) if result else None


# def get_user_points(app_user_id):
#     query = text("""
#         SELECT * FROM user_points
#         WHERE app_user_id = :user_id
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {"user_id": app_user_id}).mappings().fetchone()
#         return dict(result) if result else None
