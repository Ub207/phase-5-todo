#!/usr/bin/env python3
"""
Migration script to add priority column to tasks table in production
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
        # Check if column exists
        check_sql = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='tasks' AND column_name='priority'
        """)

        result = conn.execute(check_sql)
        exists = result.fetchone() is not None

        if exists:
            print("[OK] Column 'priority' already exists!")
        else:
            print("Adding 'priority' column to tasks table...")

            # Add priority column with default value
            add_column_sql = text("""
                ALTER TABLE tasks
                ADD COLUMN priority VARCHAR DEFAULT 'medium'
            """)

            conn.execute(add_column_sql)
            conn.commit()

            print("[OK] Successfully added 'priority' column!")
            print("   Default value: 'medium'")

            # Create index on priority for better query performance
            print("Creating index on priority column...")
            create_index_sql = text("""
                CREATE INDEX IF NOT EXISTS idx_tasks_priority
                ON tasks(priority)
            """)

            conn.execute(create_index_sql)
            conn.commit()

            print("[OK] Index created successfully!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    exit(1)

print("\n[OK] Migration completed successfully!")
print("The tasks table now has the 'priority' column.")
