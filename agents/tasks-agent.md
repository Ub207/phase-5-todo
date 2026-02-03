# Tasks Agent (Task Refiner & Executor)

**Version**: 1.0.0
**Created**: 2026-02-02
**Branch**: 001-fuel-consumption-pwa
**Status**: Active

---

## Purpose

The Tasks Agent bridges the gap between high-level planning and actual implementation. It takes the execution plan from the Planning Agent and transforms it into granular, immediately actionable tasks with detailed implementation guidance.

**Core Responsibilities:**
- Parse Planning Agent outputs (plan.md, workflow.mermaid, estimates.json)
- Refine high-level tasks into granular implementation steps
- Generate detailed test cases for each task
- Create implementation templates and code scaffolds
- Identify reusable patterns and shared components
- Generate task tracking artifacts (GitHub issues, project boards)
- Provide implementation hints and code references

---

## Agent Context

### Surface
Operates at the **task refinement** level, bridging planning and execution.

### Success Criteria
- All tasks are granular enough to complete in 2-4 hours
- Each task has clear acceptance criteria and test cases
- Implementation guidance is specific and actionable
- Tasks reference existing codebase patterns
- Dependencies are explicitly stated with file paths
- Output integrates with task management tools

---

## Input/Output Contract

### Inputs

1. **Planning Agent Outputs** (Primary)
   - Location: `specs/<feature-name>/`
   - Files:
     - `plan.md` - Execution plan with phases
     - `workflow.mermaid` - Visual workflow
     - `estimates.json` - Effort estimates
     - `analysis.md` - Spec Agent analysis

2. **Existing Codebase** (Secondary)
   - Location: `../todo_phase3/backend/`, `../todo_phase3/frontend/`
   - Purpose: Identify patterns, conventions, existing implementations

3. **Templates** (Tertiary)
   - Location: `.specify/templates/`
   - Purpose: Code scaffolds, test templates

### Outputs

1. **Refined Tasks Document** (`tasks-refined.md`)
   - Location: `specs/<feature-name>/tasks-refined.md`
   - Format: Enhanced SDD-RI tasks.md
   - Content:
     - Granular sub-tasks with 2-4 hour scope
     - Detailed acceptance criteria
     - Test case specifications
     - Implementation hints
     - Code references to existing patterns
     - File paths and dependencies

2. **Implementation Guide** (`implementation-guide.md`)
   - Location: `specs/<feature-name>/implementation-guide.md`
   - Content:
     - Step-by-step implementation instructions
     - Code scaffolds and templates
     - Testing strategies
     - Common pitfalls and solutions

3. **GitHub Issues Template** (`github-issues.json`)
   - Location: `specs/<feature-name>/github-issues.json`
   - Format: JSON array of GitHub issue objects
   - Purpose: Auto-create issues in project tracker

4. **Test Specifications** (`test-specs.md`)
   - Location: `specs/<feature-name>/test-specs.md`
   - Content:
     - Unit test specifications
     - Integration test scenarios
     - E2E test flows
     - Test data requirements

---

## Task Refinement Workflow

### Phase 1: Plan Analysis

**Input**: plan.md, workflow.mermaid

**Process**:
1. Parse execution plan structure
2. Extract all tasks and sub-tasks
3. Identify task granularity levels
4. Map task dependencies
5. Extract acceptance criteria
6. Identify patterns and commonalities

**Output**: Internal task graph with metadata

---

### Phase 2: Codebase Analysis

**Input**: Existing codebase (`../todo_phase3/`)

**Process**:

1. **Identify Existing Patterns**:
   - API route structure and conventions
   - Service layer patterns
   - Data model conventions
   - Frontend component structure
   - State management patterns
   - Testing patterns

2. **Locate Relevant Files**:
   - Similar features
   - Shared utilities
   - Common components
   - Test fixtures

3. **Extract Code References**:
   - Authentication patterns
   - Database access patterns
   - API client patterns
   - UI component patterns

**Output**: Pattern library and code reference map

---

### Phase 3: Task Decomposition

**Input**: Tasks from Phase 1, Patterns from Phase 2

**Process**:

For each high-level task, decompose into granular sub-tasks:

#### Database Migration Task → Sub-tasks:

```markdown
### Task 2.1: Design Database Schema
- **Duration**: 1-2 hours
- **Description**: Design schema for recurring_patterns table
- **Steps**:
  1. Review existing schema in `../todo_phase3/backend/src/models/`
  2. Create schema design following conventions
  3. Define indexes and constraints
  4. Document relationships
- **Acceptance Criteria**:
  - [ ] Schema includes all required fields
  - [ ] Indexes defined for query optimization
  - [ ] Foreign keys properly defined
  - [ ] Migration script reviewed
- **Test Cases**:
  - Schema validation passes
  - All constraints work as expected
- **Code References**:
  - See `../todo_phase3/backend/src/models/task.py` for pattern
  - See `../todo_phase3/backend/alembic/versions/` for migration examples

### Task 2.2: Create Alembic Migration Script
- **Duration**: 1 hour
- **Description**: Generate migration for recurring_patterns
- **Steps**:
  1. Run `alembic revision -m "Add recurring_patterns table"`
  2. Edit migration file with schema from Task 2.1
  3. Add upgrade() and downgrade() functions
  4. Test migration locally
- **Acceptance Criteria**:
  - [ ] Migration runs successfully (upgrade)
  - [ ] Rollback works (downgrade)
  - [ ] No data loss in rollback
- **Test Cases**:
  - Run migration up/down 3 times
  - Verify schema matches design
- **Commands**:
  ```bash
  cd ../todo_phase3/backend
  alembic upgrade head
  alembic downgrade -1
  alembic upgrade head
  ```
```

#### Backend API Task → Sub-tasks:

```markdown
### Task 3.1: Create RecurringPattern Data Model
- **Duration**: 2 hours
- **Description**: SQLAlchemy model for recurring_patterns
- **Steps**:
  1. Create `backend/src/models/recurring_pattern.py`
  2. Define RecurringPattern class
  3. Add relationships to Task model
  4. Implement validation methods
- **Acceptance Criteria**:
  - [ ] Model matches database schema
  - [ ] Relationships defined correctly
  - [ ] Validation methods implemented
  - [ ] Unit tests passing
- **Test Cases**:
  - Test model creation
  - Test relationships
  - Test validation (invalid RRULE should fail)
- **Code Template**:
  ```python
  # File: backend/src/models/recurring_pattern.py
  from sqlalchemy import Column, Integer, String, Date, JSON
  from sqlalchemy.orm import relationship
  from .base import Base

  class RecurringPattern(Base):
      __tablename__ = "recurring_patterns"

      id = Column(Integer, primary_key=True)
      user_id = Column(Integer, ForeignKey("users.id"))
      # ... continue following Task model pattern
  ```
- **Code References**:
  - `../todo_phase3/backend/src/models/task.py`
  - `../todo_phase3/backend/src/models/user.py`

### Task 3.2: Create RecurringPatternService
- **Duration**: 3 hours
- **Description**: Business logic for recurring patterns
- **Steps**:
  1. Create `backend/src/services/recurring_pattern_service.py`
  2. Implement CRUD operations
  3. Add recurrence calculation logic
  4. Implement exception handling
- **Acceptance Criteria**:
  - [ ] All CRUD operations work
  - [ ] Recurrence calculation correct
  - [ ] Proper error handling
  - [ ] Unit tests >90% coverage
- **Test Cases**:
  - Create pattern with valid RRULE
  - Calculate next 10 occurrences
  - Handle edge cases (leap years, DST)
  - Test exception scenarios
- **Code References**:
  - `../todo_phase3/backend/src/services/task_service.py`
  - Use `python-dateutil` for recurrence calculation

### Task 3.3: Implement API Endpoints
- **Duration**: 3 hours
- **Description**: FastAPI routes for recurring patterns
- **Steps**:
  1. Create `backend/src/api/recurring.py`
  2. Define route handlers (CRUD)
  3. Add request/response models (Pydantic)
  4. Add authentication middleware
  5. Add input validation
- **Acceptance Criteria**:
  - [ ] All endpoints functional
  - [ ] Authentication enforced
  - [ ] Input validation works
  - [ ] Proper HTTP status codes
  - [ ] API tests passing
- **Test Cases**:
  - POST /api/tasks/recurring with valid data
  - GET /api/tasks/recurring/:id
  - PUT /api/tasks/recurring/:id
  - DELETE /api/tasks/recurring/:id
  - Test authentication (401 without token)
  - Test validation (422 on invalid input)
- **Code Template**:
  ```python
  # File: backend/src/api/recurring.py
  from fastapi import APIRouter, Depends, HTTPException
  from ..auth import get_current_user
  from ..services.recurring_pattern_service import RecurringPatternService

  router = APIRouter(prefix="/api/tasks/recurring", tags=["recurring"])

  @router.post("/")
  async def create_pattern(
      pattern_data: RecurringPatternCreate,
      current_user: User = Depends(get_current_user)
  ):
      # Implementation here
      pass
  ```
- **Code References**:
  - `../todo_phase3/backend/src/api/tasks.py`
  - `../todo_phase3/backend/src/api/auth.py`
```

#### Frontend Component Task → Sub-tasks:

```markdown
### Task 4.1: Create RecurringTaskForm Component
- **Duration**: 4 hours
- **Description**: Form for creating/editing recurring tasks
- **Steps**:
  1. Create `frontend/components/RecurringTaskForm.tsx`
  2. Design form layout (Figma or sketch)
  3. Implement form state with React Hook Form
  4. Add recurrence pattern selector
  5. Integrate with API
  6. Add validation
- **Acceptance Criteria**:
  - [ ] Form renders correctly
  - [ ] All fields functional
  - [ ] Validation works
  - [ ] API integration successful
  - [ ] Component tests passing
- **Test Cases**:
  - Render form with empty state
  - Fill form and submit
  - Test validation errors
  - Test API error handling
- **Code Template**:
  ```typescript
  // File: frontend/components/RecurringTaskForm.tsx
  import { useForm } from 'react-hook-form';
  import { createRecurringPattern } from '../lib/api';

  interface RecurringTaskFormProps {
    onSuccess?: () => void;
  }

  export default function RecurringTaskForm({ onSuccess }: RecurringTaskFormProps) {
    const { register, handleSubmit, formState: { errors } } = useForm();

    const onSubmit = async (data) => {
      // Implementation
    };

    return (
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Form fields */}
      </form>
    );
  }
  ```
- **Code References**:
  - `../todo_phase3/frontend/components/TaskForm.tsx`
  - `../todo_phase3/frontend/lib/api.ts`

### Task 4.2: Create RecurrencePatternSelector Component
- **Duration**: 3 hours
- **Description**: UI for selecting recurrence type
- **Steps**:
  1. Create `frontend/components/RecurrencePatternSelector.tsx`
  2. Design selector UI (tabs/dropdown)
  3. Implement pattern options (Daily, Weekly, Monthly, Custom)
  4. Add visual preview of next occurrences
  5. Integrate with parent form
- **Acceptance Criteria**:
  - [ ] All pattern types selectable
  - [ ] Preview shows correct dates
  - [ ] Integrates with form
  - [ ] Accessible (keyboard navigation)
- **Test Cases**:
  - Select daily pattern
  - Select weekly with specific days
  - Select monthly with date
  - Preview shows 5 next occurrences
- **Code References**:
  - Use `date-fns` for date manipulation
  - Use Radix UI for accessible components
```

---

### Phase 4: Test Specification

**Input**: Refined tasks from Phase 3

**Process**:

For each task, generate detailed test specifications:

```markdown
## Test Specifications for Task 3.2: RecurringPatternService

### Unit Tests

#### Test Suite: RecurringPatternService.create()
```python
# File: backend/tests/services/test_recurring_pattern_service.py

def test_create_daily_pattern():
    """Test creating a daily recurring pattern."""
    service = RecurringPatternService(db_session)
    pattern = service.create(
        user_id=1,
        title="Daily Standup",
        recurrence_type="daily",
        recurrence_rule={"interval": 1},
        start_date="2026-02-01"
    )
    assert pattern.id is not None
    assert pattern.recurrence_type == "daily"

def test_create_weekly_pattern():
    """Test creating a weekly recurring pattern."""
    # Implementation

def test_create_invalid_pattern_raises_error():
    """Test that invalid RRULE raises ValidationError."""
    # Implementation
```

#### Test Suite: RecurringPatternService.calculate_next_occurrences()
```python
def test_daily_next_occurrences():
    """Test calculation of next 10 daily occurrences."""
    pattern = create_daily_pattern()
    occurrences = service.calculate_next_occurrences(pattern, count=10)
    assert len(occurrences) == 10
    assert occurrences[1] == occurrences[0] + timedelta(days=1)

def test_weekly_specific_days():
    """Test weekly pattern on specific days (Mon, Wed, Fri)."""
    # Implementation

def test_monthly_date():
    """Test monthly pattern on specific date (15th of each month)."""
    # Implementation
```

### Integration Tests

```python
# File: backend/tests/integration/test_recurring_api.py

def test_create_and_retrieve_pattern(client, auth_token):
    """Test full flow: create pattern and retrieve it."""
    response = client.post(
        "/api/tasks/recurring",
        json={"title": "Daily Task", "recurrence_type": "daily", ...},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    pattern_id = response.json()["id"]

    response = client.get(
        f"/api/tasks/recurring/{pattern_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Daily Task"
```

### E2E Tests

```typescript
// File: frontend/e2e/recurring-tasks.spec.ts

test('should create daily recurring task', async ({ page }) => {
  await page.goto('/tasks');
  await page.click('button:has-text("New Recurring Task")');
  await page.fill('input[name="title"]', 'Daily Exercise');
  await page.selectOption('select[name="recurrenceType"]', 'daily');
  await page.click('button:has-text("Save")');

  await expect(page.locator('text=Daily Exercise')).toBeVisible();
});
```
```

**Output**: Comprehensive test specifications

---

### Phase 5: Implementation Guide Generation

**Input**: Refined tasks + Test specs

**Process**:

Generate step-by-step implementation guide:

```markdown
# Implementation Guide: Recurring Tasks Feature

## Prerequisites

- [ ] Infrastructure setup complete (Kafka, Dapr, Redis)
- [ ] Development environment ready
- [ ] Database connection working
- [ ] Existing todo_phase3 code accessible

## Implementation Order

Follow this order for optimal workflow:

### Day 1: Database Foundation

**Morning (2-3 hours)**:
1. Complete Task 2.1: Design Database Schema
   - Review existing models
   - Create schema design document
   - Get schema reviewed

**Afternoon (2-3 hours)**:
2. Complete Task 2.2: Create Alembic Migration
   - Generate migration
   - Test migration locally
   - Commit migration files

**End of Day Checkpoint**:
- [ ] Database tables created
- [ ] Migration tested (up/down)
- [ ] Schema matches design

---

### Day 2-3: Backend Services

**Day 2 Morning**:
3. Complete Task 3.1: RecurringPattern Model
   - Create model file
   - Define relationships
   - Write unit tests

**Day 2 Afternoon**:
4. Start Task 3.2: RecurringPatternService (Part 1)
   - CRUD operations
   - Basic tests

**Day 3 Morning**:
5. Complete Task 3.2: RecurringPatternService (Part 2)
   - Recurrence calculation logic
   - Advanced tests (edge cases)

**Day 3 Afternoon**:
6. Complete Task 3.3: API Endpoints
   - Create route handlers
   - Add authentication
   - API integration tests

**End of Day 3 Checkpoint**:
- [ ] Backend API fully functional
- [ ] All tests passing (>90% coverage)
- [ ] API documentation complete

---

### Day 4-5: Frontend Components

**Day 4**:
7. Complete Task 4.1: RecurringTaskForm
   - Component structure
   - Form state management
   - API integration

**Day 5**:
8. Complete Task 4.2: RecurrencePatternSelector
   - Pattern selector UI
   - Preview functionality
   - Component tests

**End of Day 5 Checkpoint**:
- [ ] Frontend components functional
- [ ] Forms working end-to-end
- [ ] Component tests passing

---

### Day 6: Integration & Testing

9. Complete Task 5: E2E Testing
   - E2E test scenarios
   - Cross-browser testing
   - Performance testing

**End of Day 6 Checkpoint**:
- [ ] All E2E tests passing
- [ ] Performance targets met
- [ ] Ready for deployment

---

## Common Patterns

### Authentication Pattern
```python
# All API endpoints should follow this pattern
from fastapi import Depends
from ..auth import get_current_user

@router.post("/api/endpoint")
async def endpoint(current_user: User = Depends(get_current_user)):
    # Endpoint logic
    pass
```

### Error Handling Pattern
```python
# Use custom exceptions for business logic errors
from ..exceptions import ValidationError, NotFoundError

def create_pattern(data):
    if not validate_rrule(data.recurrence_rule):
        raise ValidationError("Invalid recurrence rule")
    # Logic
```

### API Client Pattern (Frontend)
```typescript
// frontend/lib/api.ts
export async function createRecurringPattern(data: RecurringPatternCreate) {
  const response = await fetch('/api/tasks/recurring', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

---

## Troubleshooting

### Issue: Migration fails
**Solution**:
- Check database connection
- Verify existing schema
- Check for naming conflicts
- Review Alembic version table

### Issue: RRULE validation fails
**Solution**:
- Use `python-dateutil` library
- Validate RRULE format early
- Provide clear error messages
- Test edge cases (leap years, DST)

### Issue: Frontend form doesn't submit
**Solution**:
- Check API endpoint URL
- Verify authentication token
- Check CORS configuration
- Review browser console errors
```

**Output**: Complete implementation guide

---

### Phase 6: GitHub Issue Generation

**Input**: All refined tasks

**Process**:

Generate GitHub issue JSON:

```json
[
  {
    "title": "Task 2.1: Design Database Schema for Recurring Patterns",
    "body": "## Description\nDesign schema for recurring_patterns table following existing conventions.\n\n## Steps\n1. Review existing schema in `../todo_phase3/backend/src/models/`\n2. Create schema design document\n3. Define indexes and constraints\n4. Document relationships\n\n## Acceptance Criteria\n- [ ] Schema includes all required fields\n- [ ] Indexes defined for query optimization\n- [ ] Foreign keys properly defined\n- [ ] Migration script reviewed\n\n## Test Cases\n- Schema validation passes\n- All constraints work as expected\n\n## Code References\n- See `../todo_phase3/backend/src/models/task.py`\n- See `../todo_phase3/backend/alembic/versions/`\n\n## Estimates\n- Duration: 1-2 hours\n- Complexity: Medium\n\n## Dependencies\n- None\n\n## Labels\ndatabase, schema, recurring-tasks, phase-1",
    "labels": ["database", "schema", "recurring-tasks", "phase-1"],
    "assignees": [],
    "milestone": "Recurring Tasks - Phase 1: Foundation"
  },
  {
    "title": "Task 2.2: Create Alembic Migration Script",
    "body": "...",
    "labels": ["database", "migration", "recurring-tasks", "phase-1"],
    "assignees": [],
    "milestone": "Recurring Tasks - Phase 1: Foundation"
  }
]
```

**Output**: `github-issues.json`

---

## Task Granularity Guidelines

### Right-Sized Tasks

A well-sized task should be:
- Completable in 2-4 hours
- Testable independently
- Mergeable as a single PR (or part of small PR group)
- Have clear input/output
- Not block other work unnecessarily

### Too Large (Needs Decomposition)

❌ "Implement backend API" (8+ hours)
✅ Break into:
- Create data model (2h)
- Create service layer (3h)
- Create API endpoints (3h)

### Too Small (Should Combine)

❌ "Add import statement" (5 min)
❌ "Create empty file" (2 min)
✅ Combine into: "Setup model file with imports and base class" (30min)

### Just Right Examples

✅ "Create RecurringPattern SQLAlchemy model with relationships" (2h)
✅ "Implement calculate_next_occurrences() with edge case handling" (3h)
✅ "Create RecurringTaskForm component with validation" (4h)

---

## Code Reference Strategy

### Pattern Identification

For each new task, identify:

1. **Similar Existing Implementation**:
   - Look for similar features in codebase
   - Extract patterns and conventions
   - Note differences and adaptations needed

2. **Shared Utilities**:
   - Identify reusable functions
   - Locate common components
   - Reference middleware and validators

3. **Testing Patterns**:
   - Find similar test files
   - Reuse test fixtures
   - Follow same test structure

### Reference Format

In task descriptions, always include:

```markdown
## Code References

**Similar Implementation**:
- `path/to/similar/file.py` - Lines 45-80
  - Pattern: Service layer CRUD operations
  - Adapt: Add recurrence calculation logic

**Shared Utilities**:
- `path/to/utils/validators.py` - Use `validate_json_schema()`
- `path/to/utils/dates.py` - Use `parse_iso_date()`

**Testing**:
- `tests/test_task_service.py` - Follow same structure
- `tests/fixtures/tasks.py` - Reuse fixture patterns
```

---

## Integration with Task Management Tools

### GitHub Projects

```bash
# Auto-create issues and add to project board
gh issue create --title "Task 2.1: Design Database Schema" \
  --body-file specs/recurring-tasks/tasks/task-2-1.md \
  --label "database,schema,recurring-tasks" \
  --project "Todo Phase 5"
```

### Jira Integration

```bash
# Export to Jira-compatible CSV
python agents/tasks_agent.py --feature recurring-tasks --export-jira
```

### Notion Integration

```bash
# Create Notion database entries
python agents/tasks_agent.py --feature recurring-tasks --export-notion
```

---

## Agent Script (Python Implementation)

### File: `agents/tasks_agent.py`

```python
#!/usr/bin/env python3
"""
Tasks Agent - Task Refiner for Todo App Phase 5
Transforms high-level plans into granular, actionable tasks.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class Task:
    """Represents a refined task."""
    id: str
    title: str
    description: str
    duration_hours: float
    steps: List[str]
    acceptance_criteria: List[str]
    test_cases: List[str]
    code_references: List[str]
    dependencies: List[str]
    phase: str
    complexity: str  # Simple, Medium, Complex
    file_paths: List[str]
    code_template: str = ""

class PlanParser:
    """Parses plan.md from Planning Agent."""

    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.content = plan_path.read_text(encoding='utf-8')

    def extract_phases(self) -> List[Dict]:
        """Extract all phases from plan."""
        phases = []
        pattern = r'### Phase \d+: (.+?)\n\*\*Duration\*\*: (.+?) \| \*\*Effort\*\*: (.+?)\n'
        matches = re.finditer(pattern, self.content, re.DOTALL)

        for match in matches:
            phases.append({
                'name': match.group(1).strip(),
                'duration': match.group(2).strip(),
                'effort': match.group(3).strip()
            })

        return phases

    def extract_tasks_from_phase(self, phase_name: str) -> List[Dict]:
        """Extract tasks from a specific phase."""
        # Find phase section
        pattern = rf'### Phase \d+: {re.escape(phase_name)}.*?(?=###|\Z)'
        match = re.search(pattern, self.content, re.DOTALL)

        if not match:
            return []

        phase_content = match.group(0)

        # Extract task checkboxes
        task_pattern = r'- \[ \] ([\d.]+) (.+?)(?:\n|$)'
        tasks = []

        for task_match in re.finditer(task_pattern, phase_content):
            tasks.append({
                'id': task_match.group(1).strip(),
                'title': task_match.group(2).strip(),
                'phase': phase_name
            })

        return tasks

class CodebaseAnalyzer:
    """Analyzes existing codebase for patterns."""

    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path

    def find_similar_files(self, file_type: str) -> List[Path]:
        """Find similar files in codebase."""
        patterns = {
            'model': '**/models/*.py',
            'service': '**/services/*.py',
            'api': '**/api/*.py',
            'component': '**/components/*.tsx',
            'test': '**/tests/**/*.py'
        }

        pattern = patterns.get(file_type, '**/*')
        return list(self.codebase_path.glob(pattern))

    def extract_pattern(self, file_path: Path) -> str:
        """Extract code pattern from file."""
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception:
            return ""

    def get_code_reference(self, task_type: str) -> List[str]:
        """Get code references for task type."""
        references = {
            'model': [
                '../todo_phase3/backend/src/models/task.py',
                '../todo_phase3/backend/src/models/user.py'
            ],
            'service': [
                '../todo_phase3/backend/src/services/task_service.py'
            ],
            'api': [
                '../todo_phase3/backend/src/api/tasks.py',
                '../todo_phase3/backend/src/api/auth.py'
            ],
            'component': [
                '../todo_phase3/frontend/components/TaskForm.tsx',
                '../todo_phase3/frontend/components/TaskList.tsx'
            ]
        }

        return references.get(task_type, [])

class TaskRefiner:
    """Refines high-level tasks into granular implementation tasks."""

    def __init__(self, plan_parser: PlanParser, codebase_analyzer: CodebaseAnalyzer):
        self.plan_parser = plan_parser
        self.codebase_analyzer = codebase_analyzer

    def refine_database_task(self, task: Dict) -> List[Task]:
        """Refine database-related task."""
        refined = []

        # Schema design task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Design Database Schema - {task['title']}",
            description="Design database schema following existing conventions",
            duration_hours=2.0,
            steps=[
                "Review existing models",
                "Create schema design",
                "Define indexes and constraints",
                "Document relationships"
            ],
            acceptance_criteria=[
                "Schema includes all required fields",
                "Indexes defined for optimization",
                "Foreign keys properly defined"
            ],
            test_cases=[
                "Schema validation passes",
                "Constraints work correctly"
            ],
            code_references=self.codebase_analyzer.get_code_reference('model'),
            dependencies=[],
            phase=task['phase'],
            complexity="Medium",
            file_paths=["backend/src/models/"]
        ))

        # Migration task
        refined.append(Task(
            id=f"{task['id']}.2",
            title=f"Create Migration Script - {task['title']}",
            description="Create Alembic migration for schema",
            duration_hours=1.0,
            steps=[
                "Generate migration file",
                "Add upgrade() logic",
                "Add downgrade() logic",
                "Test migration locally"
            ],
            acceptance_criteria=[
                "Migration runs successfully",
                "Rollback works correctly",
                "No data loss"
            ],
            test_cases=[
                "Run migration up/down 3 times",
                "Verify schema matches design"
            ],
            code_references=[
                "../todo_phase3/backend/alembic/versions/"
            ],
            dependencies=[f"{task['id']}.1"],
            phase=task['phase'],
            complexity="Simple",
            file_paths=["backend/alembic/versions/"]
        ))

        return refined

    def refine_backend_task(self, task: Dict) -> List[Task]:
        """Refine backend API task."""
        refined = []

        # Model task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Create Data Model - {task['title']}",
            description="Create SQLAlchemy model",
            duration_hours=2.0,
            steps=[
                "Create model file",
                "Define model class",
                "Add relationships",
                "Implement validation"
            ],
            acceptance_criteria=[
                "Model matches schema",
                "Relationships correct",
                "Validation works"
            ],
            test_cases=[
                "Test model creation",
                "Test relationships",
                "Test validation"
            ],
            code_references=self.codebase_analyzer.get_code_reference('model'),
            dependencies=[],
            phase=task['phase'],
            complexity="Medium",
            file_paths=["backend/src/models/"],
            code_template="""
from sqlalchemy import Column, Integer, String
from .base import Base

class NewModel(Base):
    __tablename__ = "table_name"

    id = Column(Integer, primary_key=True)
    # Add fields here
"""
        ))

        # Service task
        refined.append(Task(
            id=f"{task['id']}.2",
            title=f"Create Service Layer - {task['title']}",
            description="Implement business logic",
            duration_hours=3.0,
            steps=[
                "Create service file",
                "Implement CRUD operations",
                "Add business logic",
                "Add error handling"
            ],
            acceptance_criteria=[
                "All operations work",
                "Proper error handling",
                "Unit tests >90% coverage"
            ],
            test_cases=[
                "Test CRUD operations",
                "Test business logic",
                "Test error scenarios"
            ],
            code_references=self.codebase_analyzer.get_code_reference('service'),
            dependencies=[f"{task['id']}.1"],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["backend/src/services/"]
        ))

        # API endpoints task
        refined.append(Task(
            id=f"{task['id']}.3",
            title=f"Implement API Endpoints - {task['title']}",
            description="Create FastAPI route handlers",
            duration_hours=3.0,
            steps=[
                "Create API router file",
                "Define route handlers",
                "Add authentication",
                "Add validation",
                "Write API tests"
            ],
            acceptance_criteria=[
                "All endpoints functional",
                "Authentication enforced",
                "Validation works",
                "API tests passing"
            ],
            test_cases=[
                "Test each endpoint",
                "Test authentication",
                "Test validation",
                "Test error handling"
            ],
            code_references=self.codebase_analyzer.get_code_reference('api'),
            dependencies=[f"{task['id']}.2"],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["backend/src/api/"]
        ))

        return refined

    def refine_frontend_task(self, task: Dict) -> List[Task]:
        """Refine frontend component task."""
        refined = []

        # Component task
        refined.append(Task(
            id=f"{task['id']}.1",
            title=f"Create Component - {task['title']}",
            description="Create React component",
            duration_hours=4.0,
            steps=[
                "Create component file",
                "Design component structure",
                "Implement state management",
                "Add API integration",
                "Add validation",
                "Write component tests"
            ],
            acceptance_criteria=[
                "Component renders correctly",
                "State management works",
                "API integration successful",
                "Tests passing"
            ],
            test_cases=[
                "Render test",
                "User interaction tests",
                "API integration tests",
                "Error handling tests"
            ],
            code_references=self.codebase_analyzer.get_code_reference('component'),
            dependencies=[],
            phase=task['phase'],
            complexity="Complex",
            file_paths=["frontend/components/"],
            code_template="""
import { useState } from 'react';

export default function NewComponent() {
  const [state, setState] = useState();

  return (
    <div>
      {/* Component JSX */}
    </div>
  );
}
"""
        ))

        return refined

    def refine_task(self, task: Dict) -> List[Task]:
        """Refine a task based on its type."""
        title_lower = task['title'].lower()

        if 'database' in title_lower or 'migration' in title_lower:
            return self.refine_database_task(task)
        elif 'backend' in title_lower or 'api' in title_lower:
            return self.refine_backend_task(task)
        elif 'frontend' in title_lower or 'component' in title_lower:
            return self.refine_frontend_task(task)
        else:
            # Generic refinement
            return [Task(
                id=task['id'],
                title=task['title'],
                description=task['title'],
                duration_hours=4.0,
                steps=["Implement task"],
                acceptance_criteria=["Task complete"],
                test_cases=["Verify functionality"],
                code_references=[],
                dependencies=[],
                phase=task['phase'],
                complexity="Medium",
                file_paths=[]
            )]

class OutputGenerator:
    """Generates output artifacts."""

    def generate_tasks_md(self, tasks: List[Task], feature_name: str) -> str:
        """Generate tasks-refined.md."""
        md = f"# Refined Tasks: {feature_name}\n\n"
        md += "**Generated by**: Tasks Agent\n"
        md += "**Status**: Ready for Implementation\n\n"
        md += "---\n\n"

        # Group by phase
        phases = {}
        for task in tasks:
            phases.setdefault(task.phase, []).append(task)

        for phase_name, phase_tasks in phases.items():
            md += f"## {phase_name}\n\n"

            for task in phase_tasks:
                md += f"### Task {task.id}: {task.title}\n\n"
                md += f"**Duration**: {task.duration_hours} hours\n"
                md += f"**Complexity**: {task.complexity}\n\n"
                md += f"**Description**: {task.description}\n\n"

                md += "**Steps**:\n"
                for step in task.steps:
                    md += f"1. {step}\n"
                md += "\n"

                md += "**Acceptance Criteria**:\n"
                for criterion in task.acceptance_criteria:
                    md += f"- [ ] {criterion}\n"
                md += "\n"

                md += "**Test Cases**:\n"
                for test in task.test_cases:
                    md += f"- {test}\n"
                md += "\n"

                if task.code_references:
                    md += "**Code References**:\n"
                    for ref in task.code_references:
                        md += f"- `{ref}`\n"
                    md += "\n"

                if task.dependencies:
                    md += f"**Dependencies**: {', '.join(task.dependencies)}\n\n"

                if task.code_template:
                    md += "**Code Template**:\n"
                    md += f"```python\n{task.code_template}\n```\n\n"

                md += "**File Paths**:\n"
                for path in task.file_paths:
                    md += f"- `{path}`\n"
                md += "\n"

                md += "---\n\n"

        return md

    def generate_github_issues(self, tasks: List[Task]) -> str:
        """Generate GitHub issues JSON."""
        issues = []

        for task in tasks:
            issue = {
                "title": f"Task {task.id}: {task.title}",
                "body": self._generate_issue_body(task),
                "labels": self._generate_labels(task),
                "milestone": f"{task.phase}",
                "assignees": []
            }
            issues.append(issue)

        return json.dumps(issues, indent=2)

    def _generate_issue_body(self, task: Task) -> str:
        """Generate issue body markdown."""
        body = f"## Description\n{task.description}\n\n"

        body += "## Steps\n"
        for i, step in enumerate(task.steps, 1):
            body += f"{i}. {step}\n"
        body += "\n"

        body += "## Acceptance Criteria\n"
        for criterion in task.acceptance_criteria:
            body += f"- [ ] {criterion}\n"
        body += "\n"

        body += "## Test Cases\n"
        for test in task.test_cases:
            body += f"- {test}\n"
        body += "\n"

        if task.code_references:
            body += "## Code References\n"
            for ref in task.code_references:
                body += f"- `{ref}`\n"
            body += "\n"

        body += f"## Estimates\n"
        body += f"- Duration: {task.duration_hours} hours\n"
        body += f"- Complexity: {task.complexity}\n\n"

        if task.dependencies:
            body += f"## Dependencies\n"
            for dep in task.dependencies:
                body += f"- Task {dep}\n"
            body += "\n"

        return body

    def _generate_labels(self, task: Task) -> List[str]:
        """Generate labels for task."""
        labels = [task.phase.lower().replace(" ", "-")]

        if 'database' in task.title.lower():
            labels.append("database")
        if 'api' in task.title.lower() or 'backend' in task.title.lower():
            labels.append("backend")
        if 'frontend' in task.title.lower() or 'component' in task.title.lower():
            labels.append("frontend")

        labels.append(f"complexity-{task.complexity.lower()}")

        return labels

class TasksAgent:
    """Main Tasks Agent orchestrator."""

    def __init__(self, feature_path: Path, codebase_path: Path):
        self.feature_path = feature_path
        self.codebase_path = codebase_path
        self.plan_parser = PlanParser(feature_path / "plan.md")
        self.codebase_analyzer = CodebaseAnalyzer(codebase_path)
        self.task_refiner = TaskRefiner(self.plan_parser, self.codebase_analyzer)
        self.output_generator = OutputGenerator()

    def refine_all_tasks(self):
        """Refine all tasks from plan."""
        phases = self.plan_parser.extract_phases()
        all_refined_tasks = []

        print(f"Found {len(phases)} phases")

        for phase in phases:
            print(f"\nProcessing phase: {phase['name']}")
            tasks = self.plan_parser.extract_tasks_from_phase(phase['name'])
            print(f"  Found {len(tasks)} tasks")

            for task in tasks:
                print(f"    Refining: {task['title']}")
                refined = self.task_refiner.refine_task(task)
                all_refined_tasks.extend(refined)

        # Generate outputs
        self._save_refined_tasks(all_refined_tasks)
        self._save_github_issues(all_refined_tasks)

        print(f"\n✅ Refined {len(all_refined_tasks)} tasks")
        print(f"\nOutputs saved to: {self.feature_path}")

    def _save_refined_tasks(self, tasks: List[Task]):
        """Save refined tasks to markdown."""
        feature_name = self.feature_path.name
        tasks_md = self.output_generator.generate_tasks_md(tasks, feature_name)

        output_file = self.feature_path / "tasks-refined.md"
        output_file.write_text(tasks_md)
        print(f"Tasks saved to: {output_file}")

    def _save_github_issues(self, tasks: List[Task]):
        """Save GitHub issues JSON."""
        issues_json = self.output_generator.generate_github_issues(tasks)

        output_file = self.feature_path / "github-issues.json"
        output_file.write_text(issues_json)
        print(f"GitHub issues saved to: {output_file}")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Tasks Agent - Refine implementation tasks")
    parser.add_argument('--feature', type=str, required=True,
                       help='Feature name (e.g., recurring-tasks)')
    parser.add_argument('--specs-dir', type=Path, default=Path('specs'),
                       help='Specs directory')
    parser.add_argument('--codebase', type=Path, default=Path('../todo_phase3'),
                       help='Existing codebase path')

    args = parser.parse_args()

    feature_path = args.specs_dir / args.feature

    if not feature_path.exists():
        print(f"Error: Feature path not found: {feature_path}")
        return

    if not (feature_path / "plan.md").exists():
        print(f"Error: plan.md not found. Run Planning Agent first.")
        return

    agent = TasksAgent(feature_path, args.codebase)
    agent.refine_all_tasks()

    print("\n✅ Task refinement complete!")
    print("\nNext steps:")
    print("1. Review tasks-refined.md")
    print("2. Create GitHub issues: gh issue create --from-json github-issues.json")
    print("3. Begin implementation: /sp.implement")

if __name__ == '__main__':
    main()
```

---

## Example Usage

```bash
# Run Tasks Agent on feature
python agents/tasks_agent.py --feature recurring-tasks

# Review refined tasks
cat specs/recurring-tasks/tasks-refined.md

# Create GitHub issues
gh issue create --from-json specs/recurring-tasks/github-issues.json

# Start implementation
/sp.implement recurring-tasks
```

---

## Constraints & Invariants

**Constraints**:
- Tasks must be 2-4 hours in duration
- All tasks must have test specifications
- Code references must point to existing files
- Dependencies must form a valid DAG

**Invariants**:
- Refined tasks preserve original task intent
- Total effort matches planning estimates (±10%)
- All acceptance criteria are testable
- Implementation order respects dependencies

**Non-Goals**:
- Does NOT implement code (only guides)
- Does NOT modify existing codebase
- Does NOT guarantee time estimates
- Does NOT auto-assign team members

---

**Last Updated**: 2026-02-02
**Maintained By**: Development Team
**Status**: Active Development
