# create_tables.py
from database import Base, engine
from models import Task, RecurringRule

# Create all tables in the database
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
