# db/connection.py

from config.db_config import get_engine, get_session

engine = get_engine()
session = get_session()
