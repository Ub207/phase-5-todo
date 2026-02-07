#!/usr/bin/env python3
"""
Fix recurring_rules table schema to match the model
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("Dropping old table...")
        conn.execute(text("DROP TABLE IF EXISTS recurring_rules CASCADE"))
        conn.commit()

        print("Creating new table with correct schema...")
        conn.execute(text("""
            CREATE TABLE recurring_rules (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title VARCHAR NOT NULL,
                description VARCHAR,
                frequency VARCHAR NOT NULL,
                interval INTEGER DEFAULT 1,
                weekdays VARCHAR,
                day_of_month INTEGER,
                priority VARCHAR DEFAULT 'medium',
                next_due DATE NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

        print("Creating indexes...")
        conn.execute(text("""
            CREATE INDEX idx_recurring_rules_user_id ON recurring_rules(user_id)
        """))
        conn.execute(text("""
            CREATE INDEX idx_recurring_rules_next_due ON recurring_rules(next_due)
        """))
        conn.commit()

        print("[OK] Table recreated successfully!")

except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
