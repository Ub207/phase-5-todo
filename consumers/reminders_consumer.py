from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "reminders",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="reminder-group"
)

print("🟢 Reminders Consumer started...")

for message in consumer:
    event = message.value
    print("📩 Reminder received:", event)
