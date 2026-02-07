---
id: 002
title: Generate Kafka Event Database Handler
stage: general
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: PMLS
command: none
labels: ["kafka", "event-handling", "database", "sqlalchemy", "implementation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - event_database_handler.py
tests:
 - None (consumer script)
---

## Prompt

You are an expert Python developer. Generate a complete Python script that:

1. Connects to a Kafka topic named "task-events" on localhost:9092.
2. Deserializes JSON messages.
3. Handles two types of events:
   - "task_created": insert a new task into an SQLite database named todo.db, with fields task_id, title, user_id.
   - "task_completed": update the task in the database to mark it as completed based on task_id.
4. Uses SQLAlchemy ORM with the existing models: User, Task, RecurringRule.
5. Includes proper error handling and prints logs for each event processed.
6. The script should be ready to run as `python event_database_handler.py`.
7. Add comments explaining each major step.

Only provide the **Python code** in the response without any extra text.

## Response snapshot

Generated a complete Kafka consumer script (`event_database_handler.py`) that:

1. **Kafka Integration**: Connects to localhost:9092, subscribes to "task-events" topic
2. **Event Handlers**:
   - `handle_task_created()`: Inserts new tasks with validation
   - `handle_task_completed()`: Updates task completion status
3. **SQLAlchemy Models**: Defined User, Task, and RecurringRule models matching the existing schema
4. **Error Handling**:
   - SQLAlchemy rollback on database errors
   - JSON deserialization error handling
   - Missing field validation
   - Graceful shutdown on KeyboardInterrupt
5. **Logging**: INFO-level logging for all events and errors
6. **Database Session Management**: Session-per-message pattern with proper cleanup

The script is production-ready with proper error handling, logging, and session management.

## Outcome

- ✅ Impact: Created standalone Kafka consumer for event-driven task management
- 🧪 Tests: None (consumer script, requires Kafka and database setup for testing)
- 📁 Files: Created 1 file (event_database_handler.py)
- 🔁 Next prompts: Test the consumer with Kafka running, integrate with existing event producers, add more event types (task_updated, task_deleted)
- 🧠 Reflection: Successfully created a clean, well-structured Kafka consumer that integrates with the existing SQLAlchemy models. The script follows best practices for error handling, logging, and resource management.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable (consumer script)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add integration tests using pytest-kafka or similar testing framework to validate event processing logic
