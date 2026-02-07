#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script

This script migrates all data from SQLite (todo.db) to PostgreSQL.
It preserves all data including users, tasks, and recurring patterns.

Usage:
    # Set PostgreSQL connection in environment
    export DATABASE_URL="postgresql://user:pass@localhost:5432/todo_phase5"

    # Run migration
    python migrate_sqlite_to_postgres.py

    # Dry run (check only, no changes)
    python migrate_sqlite_to_postgres.py --dry-run
"""

import os
import sys
import argparse
from datetime import datetime
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import models
from models import Base, User, Task, RecurringPattern


class DatabaseMigrator:
    """Handles migration from SQLite to PostgreSQL"""

    def __init__(self, sqlite_path: str, postgres_url: str, dry_run: bool = False):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.dry_run = dry_run
        self.stats = {
            'users': 0,
            'tasks': 0,
            'recurring_patterns': 0,
            'errors': []
        }

    def connect_databases(self):
        """Create connections to both databases"""
        print("\n📡 Connecting to databases...")

        # SQLite connection
        sqlite_url = f"sqlite:///{self.sqlite_path}"
        self.sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        self.SqliteSession = sessionmaker(bind=self.sqlite_engine)

        # PostgreSQL connection
        self.postgres_engine = create_engine(
            self.postgres_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        self.PostgresSession = sessionmaker(bind=self.postgres_engine)

        print(f"✅ SQLite: {sqlite_url}")
        print(f"✅ PostgreSQL: {self.postgres_url.split('@')[1] if '@' in self.postgres_url else self.postgres_url}")

    def verify_sqlite_data(self):
        """Check SQLite database and report what's available"""
        print("\n🔍 Analyzing SQLite database...")

        inspector = inspect(self.sqlite_engine)
        tables = inspector.get_table_names()

        print(f"   Tables found: {', '.join(tables)}")

        sqlite_session = self.SqliteSession()
        try:
            user_count = sqlite_session.query(User).count()
            task_count = sqlite_session.query(Task).count()

            # Check if recurring_patterns table exists
            recurring_count = 0
            if 'recurring_patterns' in tables:
                recurring_count = sqlite_session.query(RecurringPattern).count()

            print(f"\n   📊 Data Summary:")
            print(f"      Users: {user_count}")
            print(f"      Tasks: {task_count}")
            print(f"      Recurring Patterns: {recurring_count}")

            return user_count > 0 or task_count > 0

        finally:
            sqlite_session.close()

    def create_postgres_tables(self):
        """Create tables in PostgreSQL"""
        print("\n🏗️  Creating PostgreSQL tables...")

        if self.dry_run:
            print("   [DRY RUN] Would create tables: users, tasks, recurring_patterns")
            return

        try:
            Base.metadata.create_all(self.postgres_engine)
            print("   ✅ Tables created successfully")
        except SQLAlchemyError as e:
            print(f"   ❌ Error creating tables: {e}")
            raise

    def migrate_users(self):
        """Migrate users from SQLite to PostgreSQL"""
        print("\n👤 Migrating users...")

        sqlite_session = self.SqliteSession()
        postgres_session = self.PostgresSession()

        try:
            users = sqlite_session.query(User).all()

            if not users:
                print("   ℹ️  No users to migrate")
                return

            if self.dry_run:
                print(f"   [DRY RUN] Would migrate {len(users)} users")
                return

            for user in users:
                # Create new user in PostgreSQL
                new_user = User(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    hashed_password=user.hashed_password,
                    created_at=user.created_at
                )
                postgres_session.merge(new_user)  # Use merge to handle existing IDs

            postgres_session.commit()
            self.stats['users'] = len(users)
            print(f"   ✅ Migrated {len(users)} users")

        except SQLAlchemyError as e:
            postgres_session.rollback()
            error_msg = f"Error migrating users: {e}"
            self.stats['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")

        finally:
            sqlite_session.close()
            postgres_session.close()

    def migrate_tasks(self):
        """Migrate tasks from SQLite to PostgreSQL"""
        print("\n📝 Migrating tasks...")

        sqlite_session = self.SqliteSession()
        postgres_session = self.PostgresSession()

        try:
            tasks = sqlite_session.query(Task).all()

            if not tasks:
                print("   ℹ️  No tasks to migrate")
                return

            if self.dry_run:
                print(f"   [DRY RUN] Would migrate {len(tasks)} tasks")
                return

            for task in tasks:
                # Create new task in PostgreSQL
                new_task = Task(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    user_id=task.user_id,
                    created_at=task.created_at,
                    due_date=task.due_date,
                    priority=task.priority if hasattr(task, 'priority') else None,
                    recurring_pattern_id=task.recurring_pattern_id if hasattr(task, 'recurring_pattern_id') else None
                )
                postgres_session.merge(new_task)

            postgres_session.commit()
            self.stats['tasks'] = len(tasks)
            print(f"   ✅ Migrated {len(tasks)} tasks")

        except SQLAlchemyError as e:
            postgres_session.rollback()
            error_msg = f"Error migrating tasks: {e}"
            self.stats['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")

        finally:
            sqlite_session.close()
            postgres_session.close()

    def migrate_recurring_patterns(self):
        """Migrate recurring patterns from SQLite to PostgreSQL"""
        print("\n🔄 Migrating recurring patterns...")

        # Check if table exists in SQLite
        inspector = inspect(self.sqlite_engine)
        if 'recurring_patterns' not in inspector.get_table_names():
            print("   ℹ️  No recurring_patterns table in SQLite")
            return

        sqlite_session = self.SqliteSession()
        postgres_session = self.PostgresSession()

        try:
            patterns = sqlite_session.query(RecurringPattern).all()

            if not patterns:
                print("   ℹ️  No recurring patterns to migrate")
                return

            if self.dry_run:
                print(f"   [DRY RUN] Would migrate {len(patterns)} recurring patterns")
                return

            for pattern in patterns:
                new_pattern = RecurringPattern(
                    id=pattern.id,
                    user_id=pattern.user_id,
                    title=pattern.title,
                    description=pattern.description,
                    frequency=pattern.frequency,
                    interval=pattern.interval,
                    days_of_week=pattern.days_of_week,
                    day_of_month=pattern.day_of_month,
                    start_date=pattern.start_date,
                    end_date=pattern.end_date,
                    last_generated=pattern.last_generated,
                    is_active=pattern.is_active,
                    created_at=pattern.created_at
                )
                postgres_session.merge(new_pattern)

            postgres_session.commit()
            self.stats['recurring_patterns'] = len(patterns)
            print(f"   ✅ Migrated {len(patterns)} recurring patterns")

        except SQLAlchemyError as e:
            postgres_session.rollback()
            error_msg = f"Error migrating recurring patterns: {e}"
            self.stats['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")

        finally:
            sqlite_session.close()
            postgres_session.close()

    def verify_migration(self):
        """Verify data was migrated correctly"""
        print("\n✔️  Verifying migration...")

        if self.dry_run:
            print("   [DRY RUN] Skipping verification")
            return True

        postgres_session = self.PostgresSession()
        try:
            pg_users = postgres_session.query(User).count()
            pg_tasks = postgres_session.query(Task).count()
            pg_patterns = postgres_session.query(RecurringPattern).count()

            print(f"   PostgreSQL counts:")
            print(f"      Users: {pg_users}")
            print(f"      Tasks: {pg_tasks}")
            print(f"      Recurring Patterns: {pg_patterns}")

            # Compare with stats
            all_match = (
                pg_users == self.stats['users'] and
                pg_tasks == self.stats['tasks'] and
                pg_patterns == self.stats['recurring_patterns']
            )

            if all_match:
                print("\n   ✅ Migration verified successfully!")
                return True
            else:
                print("\n   ⚠️  Count mismatch detected!")
                return False

        finally:
            postgres_session.close()

    def print_summary(self, start_time):
        """Print migration summary"""
        duration = datetime.now() - start_time

        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)

        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No changes were made")

        print(f"\n✅ Migrated:")
        print(f"   Users: {self.stats['users']}")
        print(f"   Tasks: {self.stats['tasks']}")
        print(f"   Recurring Patterns: {self.stats['recurring_patterns']}")
        print(f"\n⏱️  Duration: {duration.total_seconds():.2f} seconds")

        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"   - {error}")

        print("\n" + "="*60)

    def run(self):
        """Execute the full migration"""
        start_time = datetime.now()

        print("\n" + "="*60)
        print("🚀 SQLITE TO POSTGRESQL MIGRATION")
        print("="*60)

        if self.dry_run:
            print("\n🔍 Running in DRY RUN mode (no changes will be made)")

        try:
            # Step 1: Connect
            self.connect_databases()

            # Step 2: Verify source data
            has_data = self.verify_sqlite_data()
            if not has_data:
                print("\n⚠️  No data found in SQLite database. Nothing to migrate.")
                return False

            # Step 3: Create target tables
            self.create_postgres_tables()

            # Step 4: Migrate data
            self.migrate_users()
            self.migrate_tasks()
            self.migrate_recurring_patterns()

            # Step 5: Verify
            success = self.verify_migration()

            # Step 6: Summary
            self.print_summary(start_time)

            return success

        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate data from SQLite to PostgreSQL')
    parser.add_argument(
        '--sqlite-path',
        default='./todo.db',
        help='Path to SQLite database file (default: ./todo.db)'
    )
    parser.add_argument(
        '--postgres-url',
        default=None,
        help='PostgreSQL connection URL (default: from DATABASE_URL env var)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no changes made)'
    )

    args = parser.parse_args()

    # Get PostgreSQL URL
    postgres_url = args.postgres_url or os.getenv('DATABASE_URL')

    if not postgres_url:
        print("❌ Error: PostgreSQL URL not provided")
        print("   Set DATABASE_URL environment variable or use --postgres-url")
        print("\nExample:")
        print('   export DATABASE_URL="postgresql://user:pass@localhost:5432/todo_phase5"')
        print("   python migrate_sqlite_to_postgres.py")
        sys.exit(1)

    # Validate PostgreSQL URL
    if not postgres_url.startswith('postgresql://') and not postgres_url.startswith('postgres://'):
        print("❌ Error: DATABASE_URL must be a PostgreSQL URL")
        print(f"   Got: {postgres_url}")
        sys.exit(1)

    # Check SQLite file exists
    if not os.path.exists(args.sqlite_path):
        print(f"❌ Error: SQLite file not found: {args.sqlite_path}")
        sys.exit(1)

    # Run migration
    migrator = DatabaseMigrator(args.sqlite_path, postgres_url, args.dry_run)
    success = migrator.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
