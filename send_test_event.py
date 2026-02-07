"""
Send test events to Kafka for testing the event_database_handler
"""
import sys
sys.path.append('.')

from api.kafka_producer import send_event
import time

# Test event 1: task_created
task_created_event = {
    "event_type": "task_created",
    "data": {
        "task_id": 999,
        "title": "Test Task from Kafka",
        "user_id": 1,
        "description": "This is a test task created via Kafka event",
        "priority": "high"
    }
}

# Test event 2: task_completed
task_completed_event = {
    "event_type": "task_completed",
    "data": {
        "task_id": 999
    }
}

print("Sending task_created event...")
send_event('task-events', task_created_event)
print(f"[OK] Sent: {task_created_event}")

time.sleep(2)

print("\nSending task_completed event...")
send_event('task-events', task_completed_event)
print(f"[OK] Sent: {task_completed_event}")

print("\n[SUCCESS] Test events sent successfully!")
