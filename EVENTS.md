# Lightweight Event System (Phase 5)

## Overview

A simple, in-memory event-driven system for task lifecycle events. Designed to be minimal, readable, and easily replaceable with Kafka/Dapr later.

## Architecture

```
┌─────────────────┐
│  Task Router    │  (routers/tasks.py)
└────────┬────────┘
         │ publishes events
         ▼
┌─────────────────┐
│   Event Bus     │  (events.py)
└────────┬────────┘
         │ notifies
         ▼
┌─────────────────┐
│ Event Handlers  │  (event_handlers.py)
└─────────────────┘
```

## Components

### 1. Event Bus (`events.py`)

**Core class:** `EventBus`
- **Thread-safe:** Uses locks for concurrent access
- **In-memory:** No external dependencies
- **Simple API:** `subscribe()` and `publish()`

**Usage:**
```python
from events import publish_event, subscribe_to_event

# Publish an event
publish_event("task_created", {"id": 1, "title": "My Task"})

# Subscribe to an event (using decorator)
@subscribe_to_event("task_created")
def my_handler(data):
    print(f"Task created: {data['title']}")
```

### 2. Event Handlers (`event_handlers.py`)

Contains all event listeners that respond to task events.

**Current handlers:**
- `on_task_created`: Logs task creation, placeholder for notifications
- `on_task_completed`: Logs task completion
- `on_task_completed_recurring_check`: Checks for recurring tasks

**Adding new handlers:**
```python
@subscribe_to_event("task_created")
def send_notification(task_data):
    # Your notification logic here
    pass
```

### 3. Integration (`routers/tasks.py`)

Events are published at key points:
- **task_created:** After successful task creation
- **task_completed:** When task.completed changes from False to True

## Events

### task_created

**Triggered:** When a new task is created

**Data structure:**
```python
{
    "id": 123,
    "title": "Task title",
    "description": "Task description",
    "priority": "high|medium|low",
    "due_date": "2026-02-10",  # ISO date string or None
    "user_id": 1,
    "created_at": "2026-02-06T12:00:00",
}
```

### task_completed

**Triggered:** When a task is marked as completed

**Data structure:**
```python
{
    "id": 123,
    "title": "Task title",
    "description": "Task description",
    "priority": "high|medium|low",
    "user_id": 1,
    "completed_at": "2026-02-06T12:30:00",
    "recurring_enabled": True,  # Boolean
    "recurring_pattern": "daily|weekly|monthly",  # or None
}
```

## Testing

Run the test script to verify the event system:

```bash
cd /path/to/todo_phase5
python test_events.py
```

**Expected output:**
- Console logs from event handlers
- Confirmation that events are firing correctly
- Multiple handlers receiving the same event

## Usage in Production

### Current Behavior

Events are processed **synchronously** in the same thread as the HTTP request. This means:
- Event handlers execute immediately
- Request waits for all handlers to complete
- Simple and predictable for logging/monitoring

### Future Considerations

When replacing with Kafka/Dapr:
1. Replace `publish_event()` calls with Kafka producer
2. Move handlers to separate consumer services
3. Events become **asynchronous** and **distributed**
4. Add retry logic and dead-letter queues

## Migration Path to Kafka/Dapr

### Step 1: Abstract the interface
```python
# events.py
class EventPublisher:
    def publish(self, event_type, data):
        raise NotImplementedError

class InMemoryPublisher(EventPublisher):
    # Current implementation
    pass

class KafkaPublisher(EventPublisher):
    def publish(self, event_type, data):
        # Kafka implementation
        pass
```

### Step 2: Use environment variable to switch
```python
import os

if os.getenv("EVENT_BUS") == "kafka":
    event_publisher = KafkaPublisher()
else:
    event_publisher = InMemoryPublisher()
```

### Step 3: Move handlers to separate service
- Package `event_handlers.py` as a separate microservice
- Subscribe to Kafka topics
- Deploy independently

## Best Practices

### ✅ DO
- Keep handlers lightweight and fast
- Log all event activity
- Handle exceptions in handlers
- Use descriptive event names
- Include relevant data in event payloads

### ❌ DON'T
- Make blocking I/O calls in handlers (current sync implementation)
- Throw unhandled exceptions (they're logged but don't crash the app)
- Publish events inside event handlers (avoid circular dependencies)
- Include sensitive data (passwords, tokens) in event payloads

## Monitoring

### Current Logging

All event activity is logged at INFO level:
```
INFO: Subscribed handler on_task_created to event 'task_created'
INFO: Publishing event 'task_created' to 1 handler(s)
INFO: [EVENT] Task created: ID=123, Title='My Task'
```

### Future Metrics (for Kafka/Dapr)

- Event publish rate
- Event processing latency
- Handler error rate
- Dead-letter queue size

## Example: Adding a New Event

1. **Publish the event** in `routers/tasks.py`:
```python
publish_event("task_deleted", {
    "id": task.id,
    "title": task.title,
    "user_id": task.user_id,
    "deleted_at": str(datetime.utcnow()),
})
```

2. **Create a handler** in `event_handlers.py`:
```python
@subscribe_to_event("task_deleted")
def on_task_deleted(task_data):
    logger.info(f"[EVENT] Task deleted: ID={task_data['id']}")
    # Your logic here
```

3. **Test it** by triggering the delete endpoint.

## Example: Multiple Handlers for One Event

The system supports multiple handlers per event:

```python
@subscribe_to_event("task_completed")
def handler_one(data):
    print("Handler 1 executed")

@subscribe_to_event("task_completed")
def handler_two(data):
    print("Handler 2 executed")
```

Both handlers will execute when `task_completed` is published.

## Safety for Deployment

✅ **Safe for existing deployment:**
- No external dependencies
- No database schema changes
- No breaking API changes
- Backwards compatible
- Graceful degradation (handlers can fail without crashing the app)

✅ **No configuration required:**
- Works out of the box
- No environment variables needed
- No setup scripts

✅ **Easy to disable:**
Simply remove the `import event_handlers` line from `routers/tasks.py` to disable all handlers.

## Summary

| Feature | Current (Phase 5) | Future (Kafka/Dapr) |
|---------|-------------------|---------------------|
| **Storage** | In-memory | Persistent queue |
| **Processing** | Synchronous | Asynchronous |
| **Reliability** | Best-effort | At-least-once |
| **Scalability** | Single instance | Distributed |
| **Complexity** | Minimal | Production-grade |
| **Dependencies** | None | Kafka/Dapr |

This event system provides immediate value (logging, monitoring) while keeping the door open for future scalability.
