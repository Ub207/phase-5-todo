
# recurring.py
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from database import db_session
from models import Task, RecurringRule

def process_recurring_tasks():
    rules = db_session.query(RecurringRule).all()
    created_tasks = []

    for rule in rules:
        if rule.next_due <= date.today():
            task = Task(title=rule.title, due_date=rule.next_due)
            db_session.add(task)
            created_tasks.append(task.title)

            if rule.type == "Daily":
                rule.next_due = rule.next_due + timedelta(days=1)
            elif rule.type == "Weekly":
                rule.next_due = rule.next_due + timedelta(weeks=1)
            elif rule.type == "Monthly":
                rule.next_due = rule.next_due + relativedelta(months=1)

    db_session.commit()
    return created_tasks
