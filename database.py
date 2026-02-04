# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use /tmp on Railway (Linux), current directory on Windows
if os.name == "nt":  # Windows
    DATABASE_URL = "sqlite:///./todo.db"
else:  # Linux/Unix (Railway)
    DATABASE_URL = "sqlite:////tmp/todo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create session lazily when needed
def get_db_session():
    return SessionLocal()

# FastAPI dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
