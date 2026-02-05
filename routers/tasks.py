# routers/tasks.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from auth_utils import get_current_user, get_db
from schemas import TaskCreate, TaskUpdate, TaskResponse
from models import User, Task
from exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def verify_user_access(user_id: int, current_user: User):
    """Verify that current user has access to the specified user_id"""
    if current_user.id != user_id:
        raise ForbiddenException(detail="You can only access your own tasks")


@router.get("/{user_id}", response_model=List[TaskResponse])
def get_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a user"""
    verify_user_access(user_id, current_user)

    tasks = db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc()).all()
    return tasks


@router.post("/{user_id}", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task for a user"""
    verify_user_access(user_id, current_user)

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        user_id=user_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.put("/{user_id}/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    verify_user_access(user_id, current_user)

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise NotFoundException(detail="Task not found")

    # Update only provided fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.completed is not None:
        task.completed = task_data.completed
        if task_data.completed and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif not task_data.completed:
            task.completed_at = None

    db.commit()
    db.refresh(task)

    return task


@router.put("/{user_id}/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as completed"""
    verify_user_access(user_id, current_user)

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise NotFoundException(detail="Task not found")

    task.completed = True
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{user_id}/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    verify_user_access(user_id, current_user)

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise NotFoundException(detail="Task not found")

    db.delete(task)
    db.commit()

    return None
