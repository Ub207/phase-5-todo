#!/usr/bin/env python3
"""
Migration script to add recurring_rules table to production database
"""
import os
from sqlalchemy import create_engine, text

# Get production database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    print("Set it with: export DATABASE_URL='your-postgresql-url'")
    exit(1)

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if table exists
        check_sql = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name='recurring_rules'
        """)

        result = conn.execute(check_sql)
        exists = result.fetchone() is not None

        if exists:
            print("[OK] Table 'recurring_rules' already exists!")
        else:
            print("Creating 'recurring_rules' table...")

            # Create recurring_rules table
            create_table_sql = text("""
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
            """)

            conn.execute(create_table_sql)
            conn.commit()

            print("[OK] Successfully created 'recurring_rules' table!")

            # Create indexes
            print("Creating indexes...")

            create_user_index = text("""
                CREATE INDEX IF NOT EXISTS idx_recurring_rules_user_id
                ON recurring_rules(user_id)
            """)

            create_next_due_index = text("""
                CREATE INDEX IF NOT EXISTS idx_recurring_rules_next_due
                ON recurring_rules(next_due)
            """)

            conn.execute(create_user_index)
            conn.execute(create_next_due_index)
            conn.commit()

            print("[OK] Indexes created successfully!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    exit(1)

print("\n[OK] Migration completed successfully!")
print("The recurring_rules table is now ready.")
