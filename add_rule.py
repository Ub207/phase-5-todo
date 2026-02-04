from datetime import date
from database import db_session
from models import RecurringRule

# Add a demo recurring rule
rule = RecurringRule(
    title="Test Daily Task",
    type="Daily",
    next_due=date.today()
)

db_session.add(rule)
db_session.commit()
print("Rule added successfully!")
