#!/usr/bin/env python3
"""
Check the structure of recurring_rules table
"""
import os
from sqlalchemy import create_engine, text, inspect

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set!")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Get table columns
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'recurring_rules'
            ORDER BY ordinal_position
        """))

        print("Columns in recurring_rules table:")
        print("-" * 80)
        for row in result:
            print(f"{row[0]:20} {row[1]:20} nullable={row[2]:5} default={row[3]}")

        print("\n" + "=" * 80)

        # Check for any constraints
        result2 = conn.execute(text("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'recurring_rules'
        """))

        print("\nConstraints:")
        print("-" * 80)
        for row in result2:
            print(f"{row[0]:40} {row[1]}")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
