# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
# Use /tmp for database in production (Railway), local dir for development
db_path = "/tmp/todo.db" if os.getenv("RAILWAY_ENVIRONMENT") else "./todo.db"
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create session lazily when needed
def get_db_session():
    return SessionLocal()
