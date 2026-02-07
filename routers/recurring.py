# routers/recurring.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from auth_utils import get_current_user, get_db
from schemas import RecurringRuleCreate, RecurringRuleUpdate, RecurringRuleResponse, TaskResponse
from models import User, RecurringRule, Task
from exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/api/tasks/recurring", tags=["Recurring Tasks"])


@router.get("/health")
def recurring_health():
    """Health check for recurring tasks router"""
    return {"status": "ok", "router": "recurring"}


def verify_rule_access(rule_id: int, current_user: User, db: Session) -> RecurringRule:
    """Verify that current user has access to the specified recurring rule"""
    rule = db.query(RecurringRule).filter(RecurringRule.id == rule_id).first()
    if not rule:
        raise NotFoundException(detail="Recurring rule not found")
    if rule.user_id != current_user.id:
        raise ForbiddenException(detail="You can only access your own recurring rules")
    return rule


def calculate_next_occurrence(rule: RecurringRule, from_date: date = None) -> date:
    """Calculate the next occurrence date for a recurring rule"""
    if from_date is None:
        from_date = rule.next_due

    if rule.frequency == "daily":
        return from_date + timedelta(days=rule.interval)

    elif rule.frequency == "weekly":
        # For weekly, advance by interval weeks
        next_date = from_date + timedelta(weeks=rule.interval)

        # If weekdays are specified, find next matching weekday
        if rule.weekdays:
            weekday_nums = [int(d) for d in rule.weekdays.split(",")]
            current_weekday = next_date.weekday()

            # Find next matching weekday
            days_ahead = None
            for target_weekday in sorted(weekday_nums):
                if target_weekday >= current_weekday:
                    days_ahead = target_weekday - current_weekday
                    break

            # If no matching weekday found this week, use first weekday next week
            if days_ahead is None:
                days_ahead = (7 - current_weekday) + weekday_nums[0]

            next_date = next_date + timedelta(days=days_ahead)

        return next_date

    elif rule.frequency == "monthly":
        # Advance by interval months
        year = from_date.year
        month = from_date.month + rule.interval

        # Handle year overflow
        while month > 12:
            month -= 12
            year += 1

        # Use specified day of month or same day
        day = rule.day_of_month if rule.day_of_month else from_date.day

        # Handle months with fewer days
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)

        return date(year, month, day)

    return from_date


@router.get("")
def get_recurring_rules(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all recurring rules for the authenticated user"""
    query = db.query(RecurringRule).filter(RecurringRule.user_id == current_user.id)

    if active_only:
        query = query.filter(RecurringRule.active == True)

    rules = query.order_by(RecurringRule.next_due.asc()).all()

    return [
        {
            "id": rule.id,
            "user_id": rule.user_id,
            "title": rule.title,
            "description": rule.description,
            "frequency": rule.frequency,
            "interval": rule.interval,
            "weekdays": rule.weekdays,
            "day_of_month": rule.day_of_month,
            "priority": rule.priority,
            "next_due": str(rule.next_due),
            "active": rule.active,
            "created_at": str(rule.created_at),
            "updated_at": str(rule.updated_at)
        }
        for rule in rules
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_recurring_rule(
    rule_data: RecurringRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring rule"""
    new_rule = RecurringRule(
        user_id=current_user.id,
        title=rule_data.title,
        description=rule_data.description,
        frequency=rule_data.frequency,
        interval=rule_data.interval,
        weekdays=rule_data.weekdays,
        day_of_month=rule_data.day_of_month,
        priority=rule_data.priority,
        next_due=rule_data.next_due,
        active=True
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return {
        "id": new_rule.id,
        "user_id": new_rule.user_id,
        "title": new_rule.title,
        "description": new_rule.description,
        "frequency": new_rule.frequency,
        "interval": new_rule.interval,
        "weekdays": new_rule.weekdays,
        "day_of_month": new_rule.day_of_month,
        "priority": new_rule.priority,
        "next_due": str(new_rule.next_due),
        "active": new_rule.active,
        "created_at": str(new_rule.created_at),
        "updated_at": str(new_rule.updated_at)
    }


@router.get("/{rule_id}", response_model=RecurringRuleResponse)
def get_recurring_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recurring rule"""
    rule = verify_rule_access(rule_id, current_user, db)
    return rule


@router.put("/{rule_id}", response_model=RecurringRuleResponse)
def update_recurring_rule(
    rule_id: int,
    rule_data: RecurringRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recurring rule"""
    rule = verify_rule_access(rule_id, current_user, db)

    # Update only provided fields
    update_data = rule_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a recurring rule"""
    rule = verify_rule_access(rule_id, current_user, db)

    db.delete(rule)
    db.commit()

    return None


@router.post("/{rule_id}/generate", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def generate_task_from_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a task from a recurring rule and update the next occurrence"""
    rule = verify_rule_access(rule_id, current_user, db)

    # Create task from rule
    new_task = Task(
        user_id=current_user.id,
        title=rule.title,
        description=rule.description,
        due_date=rule.next_due,
        priority=rule.priority,
        completed=False
    )

    # Calculate next occurrence
    next_occurrence = calculate_next_occurrence(rule)
    rule.next_due = next_occurrence

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.post("/generate-due", response_model=List[TaskResponse])
def generate_due_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate tasks from all active recurring rules that are due"""
    today = date.today()

    # Get all active rules where next_due <= today
    due_rules = db.query(RecurringRule).filter(
        RecurringRule.user_id == current_user.id,
        RecurringRule.active == True,
        RecurringRule.next_due <= today
    ).all()

    created_tasks = []

    for rule in due_rules:
        # Create task from rule
        new_task = Task(
            user_id=current_user.id,
            title=rule.title,
            description=rule.description,
            due_date=rule.next_due,
            priority=rule.priority,
            completed=False
        )

        # Calculate next occurrence
        next_occurrence = calculate_next_occurrence(rule)
        rule.next_due = next_occurrence

        db.add(new_task)
        created_tasks.append(new_task)

    if created_tasks:
        db.commit()
        for task in created_tasks:
            db.refresh(task)

    return created_tasks
