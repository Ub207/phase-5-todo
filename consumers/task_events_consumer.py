
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "task-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="task-event-group"
)

print("🟢 Task Events Consumer started...")

for message in consumer:
    event = message.value
    print("📩 Event received:", event)

    if event["type"] == "task_created":
        print(f"✅ New task created: {event['title']}")

    if event["type"] == "task_completed":
        print(f"🎉 Task completed: {event['task_id']}")
