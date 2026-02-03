---
name: recurring-tasks
category: task-management
priority: high
dependencies: []
---

# Recurring Tasks Feature Specification

## Description

Enable users to create tasks that automatically recur based on defined patterns (daily, weekly, monthly, custom intervals). The system should generate task instances automatically and handle skip/postpone operations.

## Overview

Recurring tasks are a common productivity feature that allows users to define a task once and have it automatically recreate itself according to a schedule. This reduces manual effort for routine tasks and ensures important recurring activities are not forgotten.

## Acceptance Criteria

- User can create a recurring task with daily pattern
- User can create a recurring task with weekly pattern (specific days)
- User can create a recurring task with monthly pattern (specific date or day-of-week)
- User can create custom recurring patterns (every N days/weeks/months)
- System automatically generates next task instance when current is completed
- User can skip a single occurrence without affecting future recurrences
- User can postpone a single occurrence
- User can edit the recurrence pattern of an existing recurring task
- User can delete a recurring task (with option to keep/delete existing instances)
- User can view all instances of a recurring task
- Recurring task instances maintain relationship to parent pattern

## Technical Requirements

### Backend

- **Database Tables**:
  - `recurring_patterns` - Stores recurrence rules
  - `task_instances` - Links tasks to their recurring patterns
  - `recurrence_exceptions` - Handles skipped/postponed occurrences

- **API Endpoints**:
  - POST /api/tasks/recurring - Create recurring task
  - GET /api/tasks/recurring/:id - Get recurring task pattern
  - PUT /api/tasks/recurring/:id - Update recurring pattern
  - DELETE /api/tasks/recurring/:id - Delete recurring pattern
  - POST /api/tasks/recurring/:id/skip - Skip next occurrence
  - POST /api/tasks/recurring/:id/postpone - Postpone occurrence

### Frontend

- **Components**:
  - RecurringTaskForm - Form for creating/editing recurring patterns
  - RecurrencePatternSelector - UI for selecting recurrence type
  - RecurringTaskList - View all recurring task patterns
  - InstanceTimeline - Visual timeline of task instances

### Event Streaming

- **Kafka Topics**:
  - `task.scheduled` - Published when task instance is scheduled
  - `task.completed` - Trigger for generating next instance
  - `task.pattern.updated` - Recurring pattern modified

### State Management

- **Dapr Statestore**: Required for tracking scheduled tasks and next generation times

## User Flows

### Creating a Recurring Task

1. User clicks "Create Recurring Task"
2. User fills in task details (title, description, etc.)
3. User selects recurrence pattern:
   - Daily: Every day, Every weekday, Every N days
   - Weekly: Specific days of week
   - Monthly: Specific date or day-of-week
   - Custom: Advanced pattern builder
4. User sets start date and optional end date/count
5. System validates pattern and creates recurring_pattern record
6. System publishes `task.scheduled` event
7. Background worker generates first task instance

### Completing a Recurring Task Instance

1. User marks task as complete
2. System publishes `task.completed` event
3. Background worker checks recurring pattern
4. Worker calculates next occurrence date
5. Worker generates next task instance
6. Worker publishes `task.scheduled` event for new instance

### Skipping an Occurrence

1. User views upcoming recurring task instance
2. User clicks "Skip This Occurrence"
3. System creates exception record
4. System generates next occurrence instead
5. Skipped instance is hidden but logged

## Database Schema

### recurring_patterns Table

```sql
CREATE TABLE recurring_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    recurrence_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'custom'
    recurrence_rule JSONB NOT NULL, -- iCalendar RRULE-like structure
    start_date DATE NOT NULL,
    end_date DATE,
    max_occurrences INTEGER,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### task_instances Table

```sql
CREATE TABLE task_instances (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    pattern_id INTEGER REFERENCES recurring_patterns(id),
    occurrence_date DATE NOT NULL,
    instance_number INTEGER NOT NULL,
    is_generated BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### recurrence_exceptions Table

```sql
CREATE TABLE recurrence_exceptions (
    id SERIAL PRIMARY KEY,
    pattern_id INTEGER NOT NULL REFERENCES recurring_patterns(id),
    occurrence_date DATE NOT NULL,
    exception_type VARCHAR(20) NOT NULL, -- 'skipped', 'postponed', 'modified'
    new_date DATE, -- For postponed instances
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Kafka Event Schemas

### task.scheduled Event

```json
{
  "event_type": "task.scheduled",
  "timestamp": "2026-02-02T10:00:00Z",
  "payload": {
    "task_id": 123,
    "pattern_id": 45,
    "occurrence_date": "2026-02-05",
    "instance_number": 12,
    "user_id": 67
  }
}
```

### task.completed Event

```json
{
  "event_type": "task.completed",
  "timestamp": "2026-02-02T14:30:00Z",
  "payload": {
    "task_id": 123,
    "pattern_id": 45,
    "completed_at": "2026-02-02T14:30:00Z",
    "user_id": 67,
    "should_generate_next": true
  }
}
```

## Dapr Components

### State Store Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: recurring-tasks-state
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: ttlInSeconds
    value: "86400"  # 24 hours
```

### Pub/Sub Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-events-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "recurring-tasks-group"
```

## Non-Functional Requirements

- **Performance**: Task instance generation should complete within 100ms
- **Reliability**: No missed occurrences due to system downtime (use durable state)
- **Scalability**: Support up to 10,000 recurring patterns per user
- **Timezone Handling**: All dates respect user's timezone settings

## Dependencies

- Kafka cluster (for event streaming)
- Redis (for Dapr state store)
- PostgreSQL (existing database)
- Dapr runtime (v1.9+)

## Migration Strategy

1. Create database tables with migrations
2. Add indexes for performance (pattern_id, occurrence_date)
3. Backfill any existing recurring-like tasks (if applicable)
4. Deploy Kafka topics
5. Deploy Dapr components
6. Deploy backend service
7. Deploy frontend components
8. Enable feature flag

## Testing Strategy

- **Unit Tests**: Recurrence calculation logic, pattern validation
- **Integration Tests**: Kafka event publishing/consuming, Dapr state operations
- **E2E Tests**: Complete user flows for create/update/delete/skip/postpone
- **Performance Tests**: Bulk task instance generation

## Open Questions

1. Should we support iCalendar RRULE format for maximum flexibility?
2. How many instances to pre-generate? (Default: 1, configurable?)
3. Should recurring patterns be shareable across users?
4. What happens to future instances if pattern is deleted?

## References

- [RFC 5545 - iCalendar](https://tools.ietf.org/html/rfc5545) (for RRULE format)
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- [Kafka Event Streaming](https://kafka.apache.org/documentation/)
