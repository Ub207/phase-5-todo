"""
Event handlers for task events.
This module contains all event listeners that respond to task lifecycle events.
Includes WebSocket broadcasting for real-time frontend updates.
"""
import logging
import asyncio
from datetime import datetime
from events import subscribe_to_event

logger = logging.getLogger(__name__)

# Import WebSocket manager (will be initialized in main.py)
from websocket_manager import manager as ws_manager


@subscribe_to_event("task_created")
def on_task_created(task_data: dict):
    """
    Handler for task creation events.
    Broadcasts to WebSocket clients for real-time updates.
    """
    logger.info(f"[EVENT] Task created: ID={task_data.get('id')}, Title='{task_data.get('title')}'")

    # Log to console
    print(f"[+] New task: {task_data.get('title')} (Priority: {task_data.get('priority', 'medium')})")

    # Future implementations:
    # - Send push notification
    # - Update analytics
    # - Sync to external calendar
    # - Trigger recurring task automation


@subscribe_to_event("task_created_realtime")
def on_task_created_realtime(task_data: dict):
    """
    Handler for real-time task creation events from Kafka.
    Broadcasts to WebSocket clients.
    """
    user_id = task_data.get('user_id')
    if not user_id:
        return

    # Broadcast to user's WebSocket connections
    message = {
        "type": "task_created",
        "data": task_data
    }

    # Run async broadcast in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast_to_user(user_id, message))
        else:
            loop.run_until_complete(ws_manager.broadcast_to_user(user_id, message))
    except Exception as e:
        logger.error(f"Error broadcasting task_created to WebSocket: {e}")


@subscribe_to_event("task_completed")
def on_task_completed(task_data: dict):
    """
    Handler for task completion events.
    Future: Trigger recurring task creation, send completion notifications.
    """
    logger.info(f"[EVENT] Task completed: ID={task_data.get('id')}, Title='{task_data.get('title')}'")

    # Log to console
    print(f"[DONE] Task completed: {task_data.get('title')} at {task_data.get('completed_at')}")

    # Future implementations:
    # - Check if task is recurring and create next occurrence
    # - Send completion notification
    # - Update user statistics
    # - Trigger achievement system


@subscribe_to_event("task_completed_realtime")
def on_task_completed_realtime(task_data: dict):
    """
    Handler for real-time task completion events from Kafka.
    Broadcasts to WebSocket clients.
    """
    user_id = task_data.get('user_id')
    if not user_id:
        # Try to get user_id from the database if not in event
        from database import SessionLocal
        from models import Task
        task_id = task_data.get('id')
        if task_id:
            db = SessionLocal()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    user_id = task.user_id
            finally:
                db.close()

    if not user_id:
        return

    # Broadcast to user's WebSocket connections
    message = {
        "type": "task_completed",
        "data": task_data
    }

    # Run async broadcast in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast_to_user(user_id, message))
        else:
            loop.run_until_complete(ws_manager.broadcast_to_user(user_id, message))
    except Exception as e:
        logger.error(f"Error broadcasting task_completed to WebSocket: {e}")


@subscribe_to_event("task_completed")
def on_task_completed_recurring_check(task_data: dict):
    """
    Check if completed task has recurring rules and handle next occurrence.
    This is a separate handler to demonstrate multiple handlers per event.
    """
    # Check if task has recurring rules
    recurring_enabled = task_data.get("recurring_enabled", False)

    if recurring_enabled:
        logger.info(f"[EVENT] Recurring task completed: ID={task_data.get('id')}. "
                   f"Pattern: {task_data.get('recurring_pattern')}")
        print(f"[RECURRING] Task completed. Next occurrence will be created.")

        # Future implementation:
        # - Calculate next occurrence date
        # - Create new task instance
        # - Link to parent recurring rule
    else:
        logger.debug(f"[EVENT] Non-recurring task completed: ID={task_data.get('id')}")


# Initialize handlers on module import
def init_handlers():
    """Initialize all event handlers. Called during app startup."""
    logger.info("Event handlers initialized")
    logger.info("Registered handlers:")
    logger.info("  - task_created: on_task_created")
    logger.info("  - task_completed: on_task_completed, on_task_completed_recurring_check")


# Auto-initialize when module is imported
init_handlers()
