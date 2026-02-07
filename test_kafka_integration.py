"""
Integration Test Script for Kafka + FastAPI Backend
Tests the complete flow: Kafka Event → Database Update → API Verification
"""
import time
import json
import sqlite3
import requests
from kafka import KafkaProducer

print("=" * 70)
print("KAFKA + FASTAPI INTEGRATION TEST")
print("=" * 70)

# Configuration
KAFKA_BROKER = "localhost:9092"
BACKEND_URL = "http://localhost:8001"  # Using port 8001
TEST_USER_ID = 1

# Step 1: Initialize Kafka Producer
print("\n[1/5] Initializing Kafka Producer...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Kafka Producer initialized")
except Exception as e:
    print(f"❌ Failed to connect to Kafka: {e}")
    print("   Make sure Kafka is running on localhost:9092")
    exit(1)

# Step 2: Check Backend Health
print("\n[2/5] Checking Backend Health...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running")
    else:
        print(f"⚠️  Backend returned status {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Backend is not accessible: {e}")
    print("   Make sure FastAPI is running: uvicorn main:app --reload")
    exit(1)

# Step 3: Send task_created event
print("\n[3/5] Sending task_created event to Kafka...")
task_id = int(time.time())  # Use timestamp as unique ID
event = {
    "event_type": "task_created",
    "data": {
        "id": task_id,
        "title": f"Integration Test Task {task_id}",
        "description": "This task was created via Kafka event for integration testing",
        "user_id": TEST_USER_ID,
        "priority": "high",
        "due_date": None
    }
}

producer.send('task-events', value=event)
producer.flush()
print(f"✅ Sent task_created event: task_id={task_id}")
print(f"   Event: {json.dumps(event, indent=2)}")

# Wait for consumer to process
print("\n   ⏳ Waiting 3 seconds for consumer to process...")
time.sleep(3)

# Step 4: Verify in Database
print("\n[4/5] Verifying task in database...")
try:
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    result = cursor.execute(
        'SELECT id, title, description, completed, priority, user_id FROM tasks WHERE id=?',
        (task_id,)
    ).fetchone()
    conn.close()

    if result:
        print("✅ Task found in database:")
        print(f"   ID: {result[0]}")
        print(f"   Title: {result[1]}")
        print(f"   Description: {result[2]}")
        print(f"   Completed: {bool(result[3])}")
        print(f"   Priority: {result[4]}")
        print(f"   User ID: {result[5]}")
    else:
        print(f"❌ Task not found in database (task_id={task_id})")
        print("   Check FastAPI logs for errors")
        exit(1)
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)

# Step 5: Send task_completed event
print("\n[5/5] Sending task_completed event to Kafka...")
event_completed = {
    "event_type": "task_completed",
    "data": {
        "id": task_id,
        "title": f"Integration Test Task {task_id}",
        "user_id": TEST_USER_ID
    }
}

producer.send('task-events', value=event_completed)
producer.flush()
print(f"✅ Sent task_completed event: task_id={task_id}")

# Wait for consumer to process
print("\n   ⏳ Waiting 3 seconds for consumer to process...")
time.sleep(3)

# Verify completion in database
print("\n   Verifying task completion in database...")
try:
    conn = sqlite3.connect('todo.db')
    cursor = conn.cursor()
    result = cursor.execute(
        'SELECT completed, completed_at FROM tasks WHERE id=?',
        (task_id,)
    ).fetchone()
    conn.close()

    if result and result[0]:
        print("✅ Task marked as completed in database:")
        print(f"   Completed: {bool(result[0])}")
        print(f"   Completed At: {result[1]}")
    else:
        print(f"❌ Task not marked as completed (task_id={task_id})")
        print("   Check FastAPI logs for errors")
        exit(1)
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)

# Success!
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\n📊 Summary:")
print(f"   - Kafka events sent: 2")
print(f"   - Database updates verified: 2")
print(f"   - Test task ID: {task_id}")
print("\n🎉 Your Kafka + FastAPI integration is working perfectly!")
print("\nNext steps:")
print("   1. Check WebSocket: curl http://localhost:8000/ws/stats")
print("   2. View all tasks: curl http://localhost:8000/api/tasks")
print("   3. Connect frontend to WebSocket for real-time updates")
print("\n")

# Cleanup
producer.close()
