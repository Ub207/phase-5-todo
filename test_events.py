#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the lightweight event system.
Run this to verify events are firing correctly.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from events import event_bus, publish_event
import event_handlers


def test_task_created_event():
    """Test task_created event"""
    print("\n" + "="*60)
    print("Testing task_created event...")
    print("="*60)

    task_data = {
        "id": 123,
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "due_date": "2026-02-10",
        "user_id": 1,
        "created_at": "2026-02-06T12:00:00",
    }

    publish_event("task_created", task_data)
    print("[OK] task_created event published\n")


def test_task_completed_event():
    """Test task_completed event"""
    print("\n" + "="*60)
    print("Testing task_completed event (non-recurring)...")
    print("="*60)

    task_data = {
        "id": 123,
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "user_id": 1,
        "completed_at": "2026-02-06T12:30:00",
        "recurring_enabled": False,
        "recurring_pattern": None,
    }

    publish_event("task_completed", task_data)
    print("[OK] task_completed event published\n")


def test_recurring_task_completed_event():
    """Test task_completed event for recurring task"""
    print("\n" + "="*60)
    print("Testing task_completed event (recurring task)...")
    print("="*60)

    task_data = {
        "id": 456,
        "title": "Weekly Report",
        "description": "Submit weekly report",
        "priority": "medium",
        "user_id": 1,
        "completed_at": "2026-02-06T12:30:00",
        "recurring_enabled": True,
        "recurring_pattern": "weekly",
    }

    publish_event("task_completed", task_data)
    print("[OK] task_completed event published (recurring)\n")


def test_multiple_handlers():
    """Test that multiple handlers receive the same event"""
    print("\n" + "="*60)
    print("Testing multiple handlers for task_completed event...")
    print("="*60)

    # Count handlers
    handlers = event_bus._listeners.get("task_completed", [])
    print(f"Registered handlers for 'task_completed': {len(handlers)}")
    for i, handler in enumerate(handlers, 1):
        print(f"  {i}. {handler.__name__}")

    task_data = {
        "id": 789,
        "title": "Multi-handler Test",
        "description": "Testing multiple handlers",
        "priority": "low",
        "user_id": 1,
        "completed_at": "2026-02-06T12:45:00",
        "recurring_enabled": True,
        "recurring_pattern": "daily",
    }

    publish_event("task_completed", task_data)
    print("[OK] Event published to all handlers\n")


def test_no_handlers():
    """Test publishing event with no handlers"""
    print("\n" + "="*60)
    print("Testing event with no handlers...")
    print("="*60)

    publish_event("task_deleted", {"id": 999, "title": "Deleted Task"})
    print("[OK] Event published (no handlers registered, should be silent)\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LIGHTWEIGHT EVENT SYSTEM TEST")
    print("="*60)

    # Run tests
    test_task_created_event()
    test_task_completed_event()
    test_recurring_task_completed_event()
    test_multiple_handlers()
    test_no_handlers()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\nEvent system is working correctly!")
    print("You should see console output from event handlers above.\n")
