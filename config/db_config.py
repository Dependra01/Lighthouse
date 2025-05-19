# config/db_config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 🛠️ Fill in your local database details
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres2"
DB_USER = "postgres"
DB_PASSWORD = "Choyal"

def get_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, echo=False)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
