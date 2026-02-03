# Todo App - Phase 5: Advanced Features

**Branch**: `001-fuel-consumption-pwa`
**Version**: 1.0.0
**Status**: Development

---

## Overview

Phase 5 extends the Todo App with advanced features including:
- Recurring tasks with flexible scheduling patterns
- Reminders and notifications
- Tag-based organization and filtering
- Advanced filters and search
- Kafka event streaming integration
- Dapr microservices support

---

## Project Structure

```
todo_phase5/
├── .claude/                    # Claude Code configuration
│   └── commands/               # Custom SDD-RI commands
├── .specify/                   # Spec-Driven Development toolkit
│   ├── memory/
│   │   └── constitution.md     # Project principles
│   └── templates/              # Document templates
├── agents/                     # Specialized analysis agents
│   ├── spec-agent.md          # Spec Agent documentation
│   └── spec_agent.py          # Spec Agent implementation
├── specs/                      # Feature specifications
│   └── recurring-tasks/        # Example feature
│       ├── spec.md            # Feature specification
│       ├── analysis.md        # Generated analysis
│       ├── dependencies.json  # Dependency map
│       └── tasks.md           # Implementation tasks
├── history/                    # Development history
│   ├── prompts/               # Prompt History Records (PHRs)
│   └── adr/                   # Architecture Decision Records
└── CLAUDE.md                   # Claude Code rules
```

---

## Quick Start

### Prerequisites

- Python 3.9+ with pip
- PyYAML library: `pip install pyyaml`
- Existing Todo Phase 3 project (in `../todo_phase3/`)

### Using Spec Agent

#### 1. Create a Feature Specification

```bash
# Create feature directory
mkdir -p specs/my-feature

# Create spec file (use template or copy example)
cp .specify/templates/spec-template.md specs/my-feature/spec.md

# Edit spec.md with your feature requirements
```

#### 2. Run Spec Agent

```bash
# Analyze specific feature
python agents/spec_agent.py --feature my-feature

# Analyze all features
python agents/spec_agent.py

# Specify custom directories
python agents/spec_agent.py --input specs/ --output output/
```

#### 3. Review Generated Artifacts

```bash
# Check feature analysis
cat specs/my-feature/analysis.md

# Review dependencies
cat specs/my-feature/dependencies.json

# Check generated tasks
cat specs/my-feature/tasks.md

# Review global dependencies (when analyzing all specs)
cat specs/dependencies.json
cat specs/shared-resources.json
```

---

## Spec Agent

### Purpose

The **Spec Agent** is a specialized analyzer that:
- Parses feature specifications from markdown files
- Identifies infrastructure dependencies (Kafka, Dapr, Database, APIs)
- Generates structured task lists with dependency ordering
- Assesses complexity and risks
- Suggests Architecture Decision Records (ADRs) for significant decisions

### Key Features

1. **Automatic Dependency Detection**:
   - Kafka topics
   - Dapr components (statestore, pubsub, bindings, secrets)
   - Database tables and migrations
   - API endpoints
   - Frontend components

2. **Risk Assessment**:
   - Complexity scoring (1-10)
   - Infrastructure dependency analysis
   - Database impact assessment

3. **Task Generation**:
   - Dependency-ordered implementation tasks
   - Clear acceptance criteria
   - Integration with SDD-RI workflow

4. **ADR Suggestions**:
   - Identifies architecturally significant decisions
   - Prompts for documentation (requires user consent)

### Example Output

For the `recurring-tasks` feature, Spec Agent generated:

**Analysis** (`analysis.md`):
- Complexity: 9/10 (High)
- Priority: High
- 11 acceptance criteria
- 3 database tables, 2 API endpoints
- ADR needed for Dapr state management

**Dependencies** (`dependencies.json`):
```json
{
  "dapr_components": ["pubsub", "statestore"],
  "db_tables": ["recurring_patterns", "task_instances", "recurrence_exceptions"],
  "api_endpoints": ["/api/tasks/recurring"],
  "shared_infrastructure": {
    "kafka": [],
    "dapr": ["pubsub", "statestore"],
    "database": ["recurring_patterns", "task_instances", "recurrence_exceptions"],
    "redis": ["recurring-tasks-redis"]
  }
}
```

**Tasks** (`tasks.md`):
- Task 1: Configure Dapr Components
- Task 2: Create Database Migrations
- Task 3: Implement Backend API (depends on Task 2)
- Task 4: Implement Frontend Components (depends on Task 3)
- Task 5: End-to-End Testing (depends on all)

---

## SDD-RI Workflow Integration

### Standard Workflow

```bash
# 1. Create specification
/sp.specify recurring-tasks "Enable users to create recurring tasks..."

# 2. Run Spec Agent for analysis
python agents/spec_agent.py --feature recurring-tasks

# 3. Review analysis and dependencies
cat specs/recurring-tasks/analysis.md
cat specs/recurring-tasks/dependencies.json

# 4. Create architecture plan
/sp.plan recurring-tasks

# 5. Generate detailed tasks
/sp.tasks recurring-tasks

# 6. Create ADRs (if suggested)
/sp.adr kafka-event-schema
/sp.adr dapr-state-management

# 7. Implement features
/sp.implement recurring-tasks

# 8. Commit and create PR
/sp.git.commit_pr
```

---

## Feature Categories

### Planned Features

1. **Recurring Tasks**
   - Daily, weekly, monthly, custom patterns
   - Auto-generation of task instances
   - Skip/postpone handling
   - iCalendar RRULE support

2. **Reminders & Notifications**
   - Time-based reminders
   - Multi-channel delivery (email, push, in-app)
   - Configurable notification preferences

3. **Tags & Categories**
   - Hierarchical tag system
   - Tag-based filtering and search
   - Tag analytics and insights

4. **Advanced Filters**
   - Complex query builder
   - Saved filter presets
   - Filter sharing and collaboration

5. **Kafka Event Streaming**
   - Task lifecycle events
   - Cross-service communication
   - Event replay capability

6. **Dapr Integration**
   - State management (Redis/PostgreSQL)
   - Pub/Sub messaging
   - Service invocation
   - Secret management

---

## Infrastructure Dependencies

### Required Services

1. **Kafka** (Event Streaming)
   - Version: 3.0+
   - Components: Zookeeper, Brokers
   - Purpose: Task events, notifications, cross-service messaging

2. **Dapr** (Microservices Platform)
   - Version: 1.9+
   - Components: Runtime, Sidecars
   - Purpose: State management, Pub/Sub, Service invocation

3. **Redis** (State Store)
   - Version: 6.0+
   - Purpose: Dapr state backing, caching

4. **PostgreSQL** (Database)
   - Version: 13+
   - Purpose: Primary data store (extends Phase 3 schema)

### Setup Instructions

#### Local Development (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.0.1
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.0.1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_pass

  dapr-placement:
    image: daprio/dapr:1.9.0
    command: ["./placement", "-port", "50006"]
    ports:
      - "50006:50006"
```

#### Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Verify Kafka
docker exec -it <kafka-container> kafka-topics --list --bootstrap-server localhost:9092

# Verify Redis
redis-cli ping

# Verify PostgreSQL
psql -h localhost -U todo_user -d todo_db -c "SELECT version();"

# Initialize Dapr
dapr init
```

---

## Testing

### Run Spec Agent Tests

```python
# Create test spec
mkdir -p specs/test-feature
cat > specs/test-feature/spec.md <<EOF
---
name: test-feature
priority: medium
---

## Description
Test feature for validation.

## Acceptance Criteria
- Should work correctly

Kafka topic: test.events
Dapr statestore required
Table: test_data
API endpoint: POST /api/test
Component: TestComponent
EOF

# Run analysis
python agents/spec_agent.py --feature test-feature

# Verify outputs
ls -la specs/test-feature/
# Expected: spec.md, analysis.md, dependencies.json, tasks.md
```

### Validate Generated Artifacts

```bash
# Check analysis completeness
grep "Complexity:" specs/test-feature/analysis.md
grep "ADR Needed" specs/test-feature/analysis.md

# Verify dependencies extracted
cat specs/test-feature/dependencies.json | jq '.features["test-feature"]'

# Check task structure
grep "## Task" specs/test-feature/tasks.md
```

---

## Development Guidelines

### Creating Good Specs

1. **Use YAML Front Matter**:
   ```yaml
   ---
   name: feature-name
   category: feature-category
   priority: high|medium|low
   dependencies: [other-feature-1, other-feature-2]
   ---
   ```

2. **Include Required Sections**:
   - Description/Overview
   - Acceptance Criteria (bulleted list)
   - Technical Requirements (optional but helpful)
   - Database Schema (if applicable)
   - API Endpoints (if applicable)

3. **Be Explicit About Dependencies**:
   - Mention "Kafka topic: topic-name" explicitly
   - Mention "Dapr statestore" or other components
   - Mention "Table: table_name" for database needs
   - Use proper HTTP method + path format: "POST /api/endpoint"

4. **Provide Context**:
   - User flows and scenarios
   - Data models and schemas
   - Event schemas (for Kafka)
   - Non-functional requirements

### Best Practices

- Start with spec creation before any implementation
- Run Spec Agent early to identify dependencies
- Review generated tasks before creating ADRs
- Keep specs updated as requirements change
- Use consistent naming conventions

---

## Common Issues

### Issue: Spec Agent doesn't detect dependencies

**Solution**: Use explicit keywords in spec:
- For Kafka: "topic:", "Kafka topic"
- For Dapr: "statestore", "pubsub", "Dapr"
- For DB: "table:", "database table"
- For API: "GET /path", "POST /path", etc.

### Issue: Generated tasks are too generic

**Solution**: Provide more detail in spec:
- Add specific API endpoint paths
- List component names explicitly
- Include data models/schemas

### Issue: Complexity score seems wrong

**Solution**: The score is heuristic-based. Consider:
- Manually adjusting in analysis.md
- Providing feedback to refine algorithm

---

## Next Steps

1. **Create Constitution**:
   ```bash
   /sp.constitution
   ```

2. **Add More Features**:
   ```bash
   # Copy spec template
   cp specs/recurring-tasks/spec.md specs/reminders/spec.md

   # Edit and analyze
   python agents/spec_agent.py --feature reminders
   ```

3. **Generate Global Dependency Map**:
   ```bash
   python agents/spec_agent.py
   cat specs/dependencies.json
   cat specs/shared-resources.json
   ```

4. **Create Architecture Plans**:
   ```bash
   /sp.plan recurring-tasks
   /sp.plan reminders
   /sp.plan tags
   ```

5. **Document Architectural Decisions**:
   ```bash
   /sp.adr kafka-topic-schema-design
   /sp.adr dapr-state-management-strategy
   /sp.adr database-migration-approach
   ```

---

## Resources

### Documentation

- [Spec Agent Documentation](agents/spec-agent.md)
- [Constitution Template](.specify/memory/constitution.md)
- [Spec Template](.specify/templates/spec-template.md)
- [Plan Template](.specify/templates/plan-template.md)
- [Tasks Template](.specify/templates/tasks-template.md)
- [ADR Template](.specify/templates/adr-template.md)

### External References

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Dapr Documentation](https://docs.dapr.io/)
- [iCalendar RRULE Spec (RFC 5545)](https://tools.ietf.org/html/rfc5545)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## Contributing

This project follows **Spec-Driven Development (SDD)** methodology:

1. Write specification first
2. Run Spec Agent for analysis
3. Create architectural plan
4. Generate implementation tasks
5. Create necessary ADRs
6. Implement with tests
7. Commit with proper PHR

---

## License

[Specify License]

---

## Contact

For questions or issues, create an issue in the project repository.

---

**Last Updated**: 2026-02-02
**Maintained By**: Development Team
