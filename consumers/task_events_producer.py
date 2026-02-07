from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

events = [
    {"type": "task_created", "task_id": 1, "title": "Buy groceries", "user_id": "user1"},
    {"type": "task_completed", "task_id": 1, "user_id": "user1"},
    {"type": "task_created", "task_id": 2, "title": "Do homework", "user_id": "user2"}
]

for event in events:
    producer.send("task-events", event)
    print("📤 Event sent:", event)
    time.sleep(1)

producer.flush()
print("✅ All events sent!")
