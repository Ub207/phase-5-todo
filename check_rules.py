from database import db_session
from models import RecurringRule
from datetime import date

rules = db_session.query(RecurringRule).all()
if not rules:
    print("No recurring rules found!")
else:
    for r in rules:
        print(r.title, r.next_due, r.type)
