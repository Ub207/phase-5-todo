# models.py
from sqlalchemy import Column, Integer, String, Date
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    due_date = Column(Date)

class RecurringRule(Base):
    __tablename__ = "recurring_rules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)  # "Daily", "Weekly", "Monthly"
    next_due = Column(Date)
