# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Always use /tmp on Railway deployment
DATABASE_URL = "sqlite:////tmp/todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create session lazily when needed
def get_db_session():
    return SessionLocal()
