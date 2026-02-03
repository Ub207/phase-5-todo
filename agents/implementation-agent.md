# Implementation Agent (Code Executor)

**Version**: 1.0.0
**Created**: 2026-02-02
**Branch**: 001-fuel-consumption-pwa
**Status**: Active

---

## Purpose

The Implementation Agent is the final agent in the SDD-RI workflow. It executes refined tasks by writing actual code, running tests, and ensuring quality standards. This agent transforms specifications and plans into working software.

**Core Responsibilities:**
- Execute refined tasks from Tasks Agent
- Write production-quality code following project conventions
- Generate comprehensive test suites
- Run tests and fix failures
- Perform code quality checks
- Create documentation
- Commit changes with proper PHRs
- Report implementation status and blockers

---

## Agent Context

### Surface
Operates at the **code execution** level, the final step in the SDD-RI workflow.

### Success Criteria
- All task acceptance criteria met
- Tests passing (>90% coverage)
- Code follows project conventions
- No linting/formatting errors
- Documentation complete
- Changes committed with PHR
- No regressions introduced

---

## Input/Output Contract

### Inputs

1. **Refined Tasks** (Primary)
   - Location: `specs/<feature-name>/tasks-refined.md`
   - Content: Granular tasks with implementation guidance

2. **Implementation Guide** (Secondary)
   - Location: `specs/<feature-name>/implementation-guide.md`
   - Content: Step-by-step instructions, code templates

3. **Existing Codebase** (Context)
   - Location: `../todo_phase3/`
   - Purpose: Follow conventions, reuse patterns

4. **Test Specifications** (Testing)
   - Location: `specs/<feature-name>/test-specs.md`
   - Purpose: Test case definitions

### Outputs

1. **Implemented Code**
   - Location: `../todo_phase3/backend/`, `../todo_phase3/frontend/`
   - Format: Production-ready code
   - Content: New features, bug fixes, refactors

2. **Test Files**
   - Location: `../todo_phase3/backend/tests/`, `../todo_phase3/frontend/tests/`
   - Format: Unit, integration, E2E tests
   - Content: Comprehensive test coverage

3. **Implementation Report** (`implementation-report.md`)
   - Location: `specs/<feature-name>/implementation-report.md`
   - Content:
     - Tasks completed
     - Tests written and results
     - Issues encountered
     - Time spent vs. estimated
     - Code metrics

4. **Prompt History Records (PHRs)**
   - Location: `history/prompts/<feature-name>/`
   - Format: PHR markdown files
   - Purpose: Development history tracking

---

## Implementation Workflow

### Phase 1: Task Selection & Planning

**Input**: tasks-refined.md

**Process**:

1. **Parse Refined Tasks**:
   - Load tasks-refined.md
   - Build task dependency graph
   - Identify ready-to-start tasks (no unmet dependencies)

2. **Select Next Task**:
   - Choose task with:
     - No unmet dependencies
     - Highest priority
     - Fits available time
   - Mark task as "in progress"

3. **Gather Context**:
   - Review task description
   - Read code references
   - Review code templates
   - Check acceptance criteria

**Output**: Selected task with full context

---

### Phase 2: Code Generation

**Input**: Selected task, code templates, references

**Process**:

#### For Backend Tasks:

```python
# Example: Implementing RecurringPattern Model

# 1. Read code references
reference_model = read_file("../todo_phase3/backend/src/models/task.py")

# 2. Extract patterns
patterns = extract_patterns(reference_model)
# - Imports structure
# - Class definition
# - Column definitions
# - Relationships
# - Validation methods

# 3. Generate new model
new_model = generate_model(
    name="RecurringPattern",
    table_name="recurring_patterns",
    columns=[
        ("id", "Integer", "primary_key=True"),
        ("user_id", "Integer", "ForeignKey('users.id')"),
        ("title", "String(255)"),
        ("recurrence_type", "String(20)"),
        ("recurrence_rule", "JSON"),
        # ... more columns
    ],
    relationships=[
        ("user", "User", "backref='recurring_patterns'"),
        ("instances", "TaskInstance", "backref='pattern'")
    ]
)

# 4. Add validation methods
new_model += generate_validation_methods([
    "validate_recurrence_rule",
    "validate_date_range"
])

# 5. Write to file
write_file("../todo_phase3/backend/src/models/recurring_pattern.py", new_model)
```

#### For Frontend Tasks:

```typescript
// Example: Implementing RecurringTaskForm Component

// 1. Read code references
const referenceComponent = readFile("../todo_phase3/frontend/components/TaskForm.tsx");

// 2. Extract patterns
const patterns = extractPatterns(referenceComponent);
// - Imports
// - Component structure
// - State management
// - Form handling
// - API integration
// - Validation

// 3. Generate new component
const newComponent = generateComponent({
  name: "RecurringTaskForm",
  props: ["onSuccess", "initialData"],
  state: [
    "formData",
    "errors",
    "loading"
  ],
  hooks: [
    "useForm",
    "useState",
    "useEffect"
  ],
  methods: [
    "handleSubmit",
    "handleValidation",
    "handleApiCall"
  ]
});

// 4. Add form fields
newComponent += generateFormFields([
  { name: "title", type: "text", required: true },
  { name: "recurrenceType", type: "select", options: ["daily", "weekly", "monthly"] },
  // ... more fields
]);

// 5. Write to file
writeFile("../todo_phase3/frontend/components/RecurringTaskForm.tsx", newComponent);
```

**Output**: Generated code files

---

### Phase 3: Test Generation

**Input**: Generated code, test specifications

**Process**:

#### Unit Tests:

```python
# Example: Tests for RecurringPattern Model

# 1. Generate test class
test_class = generate_test_class(
    name="TestRecurringPatternModel",
    target="RecurringPattern",
    test_file="test_recurring_pattern_model.py"
)

# 2. Generate test methods from specifications
tests = [
    generate_test_method(
        name="test_create_daily_pattern",
        description="Test creating a daily recurring pattern",
        setup=[
            "Create test user",
            "Prepare pattern data"
        ],
        execution=[
            "Create pattern with daily recurrence",
            "Save to database"
        ],
        assertions=[
            "Pattern ID is not None",
            "Recurrence type is 'daily'",
            "User relationship works"
        ]
    ),
    generate_test_method(
        name="test_validate_recurrence_rule",
        description="Test RRULE validation",
        setup=["Prepare invalid RRULE"],
        execution=["Attempt to create pattern"],
        assertions=["ValidationError raised"]
    ),
    # ... more tests
]

# 3. Add fixtures
fixtures = generate_fixtures([
    "sample_user",
    "sample_daily_pattern",
    "sample_weekly_pattern"
])

# 4. Combine and write
test_file = test_class + fixtures + join(tests)
write_file("../todo_phase3/backend/tests/models/test_recurring_pattern_model.py", test_file)
```

#### Integration Tests:

```python
# Example: API Integration Tests

tests = [
    generate_integration_test(
        name="test_create_and_retrieve_pattern",
        description="Test full CRUD flow",
        steps=[
            "Authenticate user",
            "POST /api/tasks/recurring with valid data",
            "Assert 201 status",
            "GET /api/tasks/recurring/:id",
            "Assert data matches"
        ]
    ),
    # ... more tests
]
```

#### E2E Tests:

```typescript
// Example: E2E Test for Recurring Tasks

test('User can create daily recurring task', async ({ page }) => {
  // 1. Navigate to tasks page
  await page.goto('/tasks');

  // 2. Open recurring task form
  await page.click('button:has-text("New Recurring Task")');

  // 3. Fill form
  await page.fill('input[name="title"]', 'Daily Exercise');
  await page.selectOption('select[name="recurrenceType"]', 'daily');
  await page.fill('input[name="startDate"]', '2026-02-05');

  // 4. Submit
  await page.click('button:has-text("Save")');

  // 5. Verify creation
  await expect(page.locator('text=Daily Exercise')).toBeVisible();
  await expect(page.locator('text=Repeats daily')).toBeVisible();
});
```

**Output**: Comprehensive test files

---

### Phase 4: Test Execution & Fixing

**Input**: Generated code and tests

**Process**:

```python
# Test execution loop

def implement_with_tdd(task):
    """Implement task using TDD approach."""
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # 1. Run tests
        result = run_tests(task)

        # 2. Check results
        if result.all_passing:
            print("✅ All tests passing!")
            break

        if result.no_failures and not result.all_passing:
            print("⚠️  Tests incomplete, continuing implementation")
            # Continue to implement more features

        if result.has_failures:
            print(f"❌ {result.failure_count} tests failing")

            # 3. Analyze failures
            failures = analyze_failures(result.failures)

            for failure in failures:
                print(f"  - {failure.test_name}: {failure.error_message}")

                # 4. Fix based on failure type
                if failure.type == "ImportError":
                    fix_import_error(failure)
                elif failure.type == "AttributeError":
                    fix_missing_attribute(failure)
                elif failure.type == "AssertionError":
                    fix_logic_error(failure)
                elif failure.type == "ValidationError":
                    fix_validation_logic(failure)
                else:
                    print(f"    Manual fix needed: {failure.type}")
                    break

            # 5. Re-run tests
            continue

        # 6. Check coverage
        if result.all_passing:
            coverage = check_coverage(task)
            if coverage < 0.90:
                print(f"⚠️  Coverage {coverage:.1%} < 90%, adding tests")
                add_missing_tests(task, coverage.missing_lines)
            else:
                print(f"✅ Coverage {coverage:.1%} >= 90%")
                break

    if iteration >= max_iterations:
        print("❌ Max iterations reached, manual intervention needed")
        return False

    return True
```

**Fixing Strategies**:

1. **Import Errors**:
   - Add missing imports
   - Check file paths
   - Verify module structure

2. **Attribute Errors**:
   - Add missing methods/properties
   - Fix typos in names
   - Check inheritance

3. **Assertion Errors**:
   - Fix business logic
   - Correct calculations
   - Update data transformations

4. **Validation Errors**:
   - Fix validation logic
   - Update constraints
   - Handle edge cases

**Output**: Working code with passing tests

---

### Phase 5: Quality Assurance

**Input**: Implemented code with passing tests

**Process**:

#### Code Quality Checks:

```bash
# Backend (Python)
# 1. Linting
python -m pylint backend/src/models/recurring_pattern.py
python -m flake8 backend/src/models/recurring_pattern.py

# 2. Type checking
python -m mypy backend/src/models/recurring_pattern.py

# 3. Security scan
bandit -r backend/src/

# 4. Code complexity
python -m radon cc backend/src/models/recurring_pattern.py

# Frontend (TypeScript)
# 1. Linting
npm run lint

# 2. Type checking
npm run type-check

# 3. Format checking
npm run format:check
```

#### Fix Quality Issues:

```python
def ensure_quality(file_path):
    """Ensure code meets quality standards."""

    # 1. Run linting
    lint_result = run_linter(file_path)

    if lint_result.has_issues:
        print(f"Linting issues found: {len(lint_result.issues)}")

        for issue in lint_result.issues:
            if issue.auto_fixable:
                apply_auto_fix(issue)
            else:
                manual_fix_linting_issue(issue)

        # Re-run linter
        lint_result = run_linter(file_path)

    # 2. Check type hints (Python)
    if file_path.endswith('.py'):
        type_result = run_mypy(file_path)

        if type_result.has_errors:
            add_type_hints(file_path, type_result.missing_hints)

    # 3. Check complexity
    complexity = check_complexity(file_path)

    for function, score in complexity.items():
        if score > 10:  # McCabe complexity threshold
            print(f"⚠️  High complexity in {function}: {score}")
            # Suggest refactoring
            suggest_refactoring(function)

    # 4. Format code
    format_code(file_path)

    print(f"✅ Quality checks passed for {file_path}")
```

**Output**: High-quality, compliant code

---

### Phase 6: Documentation

**Input**: Implemented and tested code

**Process**:

#### Code Documentation:

```python
def add_documentation(file_path, code_type):
    """Add docstrings and comments to code."""

    if code_type == "model":
        add_model_documentation(file_path)
    elif code_type == "service":
        add_service_documentation(file_path)
    elif code_type == "api":
        add_api_documentation(file_path)

def add_model_documentation(file_path):
    """Add docstrings to model classes."""

    # 1. Class docstring
    add_docstring(
        target="RecurringPattern",
        docstring="""
        Represents a recurring pattern for tasks.

        Attributes:
            id (int): Primary key
            user_id (int): Foreign key to users table
            title (str): Pattern title
            recurrence_type (str): Type of recurrence (daily, weekly, monthly)
            recurrence_rule (dict): iCalendar RRULE-like structure
            start_date (date): Start date for recurrences
            end_date (date, optional): End date for recurrences

        Example:
            >>> pattern = RecurringPattern(
            ...     user_id=1,
            ...     title="Daily Standup",
            ...     recurrence_type="daily",
            ...     recurrence_rule={"interval": 1},
            ...     start_date=date.today()
            ... )
        """
    )

    # 2. Method docstrings
    add_docstring(
        target="validate_recurrence_rule",
        docstring="""
        Validate the recurrence rule format.

        Args:
            rule (dict): Recurrence rule to validate

        Returns:
            bool: True if valid, False otherwise

        Raises:
            ValidationError: If rule format is invalid
        """
    )
```

#### README Updates:

```python
def update_readme(feature_name, implemented_files):
    """Update README with new feature info."""

    readme_content = f"""
## {feature_name.replace('-', ' ').title()}

### Description
{get_feature_description(feature_name)}

### Usage

#### Backend API
```python
# Create recurring pattern
from src.services.recurring_pattern_service import RecurringPatternService

service = RecurringPatternService(db)
pattern = service.create(
    user_id=1,
    title="Daily Task",
    recurrence_type="daily",
    recurrence_rule={{"interval": 1}},
    start_date="2026-02-05"
)
```

#### Frontend Components
```typescript
import RecurringTaskForm from '@/components/RecurringTaskForm';

<RecurringTaskForm
  onSuccess={() => console.log('Pattern created!')}
/>
```

### API Endpoints

- `POST /api/tasks/recurring` - Create recurring pattern
- `GET /api/tasks/recurring/:id` - Get pattern by ID
- `PUT /api/tasks/recurring/:id` - Update pattern
- `DELETE /api/tasks/recurring/:id` - Delete pattern

### Database Schema

See migration: `backend/alembic/versions/xxxx_add_recurring_patterns.py`

### Tests

- Unit tests: `backend/tests/models/test_recurring_pattern_model.py`
- Service tests: `backend/tests/services/test_recurring_pattern_service.py`
- API tests: `backend/tests/integration/test_recurring_api.py`
- E2E tests: `frontend/e2e/recurring-tasks.spec.ts`
"""

    append_to_readme(readme_content)
```

**Output**: Well-documented code

---

### Phase 7: Commit & PHR

**Input**: Completed, tested, documented code

**Process**:

```python
def commit_changes(task, files_changed):
    """Commit changes with proper PHR."""

    # 1. Stage files
    for file_path in files_changed:
        git_add(file_path)

    # 2. Generate commit message
    commit_message = generate_commit_message(task)
    """
    feat: Add RecurringPattern model and service

    Implements Task 3.1 and 3.2 from recurring-tasks feature.

    - Created RecurringPattern SQLAlchemy model
    - Implemented RecurringPatternService with CRUD operations
    - Added recurrence calculation logic
    - Added comprehensive unit tests (95% coverage)

    Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
    """

    # 3. Commit
    git_commit(commit_message)

    # 4. Create PHR
    create_phr(
        task=task,
        files=files_changed,
        commit_hash=get_last_commit_hash(),
        stage="implementation"
    )

    print(f"✅ Committed {len(files_changed)} files with PHR")
```

**Output**: Changes committed with PHR

---

### Phase 8: Status Reporting

**Input**: Task completion data

**Process**:

```python
def generate_implementation_report(task, metrics):
    """Generate implementation report."""

    report = f"""
# Implementation Report: {task.title}

## Task Details
- **ID**: {task.id}
- **Title**: {task.title}
- **Estimated Duration**: {task.duration_hours} hours
- **Actual Duration**: {metrics.actual_hours} hours
- **Variance**: {metrics.variance}%

## Implementation Summary

### Files Created
{generate_file_list(metrics.files_created)}

### Files Modified
{generate_file_list(metrics.files_modified)}

### Tests Written
- Unit tests: {metrics.unit_tests_count}
- Integration tests: {metrics.integration_tests_count}
- E2E tests: {metrics.e2e_tests_count}
- **Total coverage**: {metrics.coverage}%

### Test Results
- ✅ Passing: {metrics.tests_passing}
- ❌ Failing: {metrics.tests_failing}
- ⏭️  Skipped: {metrics.tests_skipped}

## Code Quality Metrics

- **Lines of Code**: {metrics.loc}
- **Cyclomatic Complexity**: {metrics.complexity} (avg)
- **Maintainability Index**: {metrics.maintainability}
- **Linting Issues**: {metrics.lint_issues}
- **Type Coverage**: {metrics.type_coverage}%

## Issues Encountered

{generate_issues_list(metrics.issues)}

## Acceptance Criteria Status

{generate_acceptance_status(task.acceptance_criteria, metrics)}

## Next Steps

{generate_next_steps(task, metrics)}

---

**Report Generated**: {datetime.now().isoformat()}
**Agent**: Implementation Agent v1.0.0
"""

    save_report(report, task.feature_path / "implementation-report.md")
```

**Output**: Implementation report

---

## Error Handling & Recovery

### Common Issues

#### Issue 1: Test Failures

**Symptoms**:
- Tests fail after initial implementation
- Assertion errors
- Logic errors

**Recovery**:
1. Analyze failure messages
2. Identify root cause
3. Fix implementation
4. Re-run tests
5. Iterate until passing

**Example**:
```python
def handle_test_failure(failure):
    """Handle test failure with retry logic."""

    if failure.type == "AssertionError":
        # Extract expected vs actual
        expected = failure.expected_value
        actual = failure.actual_value

        # Analyze difference
        diff = compare_values(expected, actual)

        # Fix based on diff
        if diff.type == "off_by_one":
            fix_off_by_one_error(failure.location)
        elif diff.type == "wrong_type":
            fix_type_conversion(failure.location)
        # ... more cases
```

#### Issue 2: Import Errors

**Symptoms**:
- Module not found
- Cannot import name
- Circular imports

**Recovery**:
1. Check file structure
2. Verify imports
3. Fix circular dependencies
4. Update __init__.py files

#### Issue 3: Database Errors

**Symptoms**:
- Migration fails
- Integrity constraint violation
- Connection errors

**Recovery**:
1. Rollback migration
2. Fix schema issues
3. Retry migration
4. Verify database state

#### Issue 4: API Errors

**Symptoms**:
- 500 Internal Server Error
- 422 Validation Error
- 401 Unauthorized

**Recovery**:
1. Check logs
2. Fix validation logic
3. Update authentication
4. Test endpoints

### Retry Strategy

```python
def implement_with_retry(task, max_retries=3):
    """Implement task with retry on failure."""

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🔄 Attempt {attempt}/{max_retries}")

            # Implement task
            result = implement_task(task)

            # Run tests
            test_result = run_tests(task)

            if test_result.all_passing:
                print("✅ Implementation successful!")
                return result

            # Tests failing, analyze and fix
            print(f"⚠️  Tests failing, analyzing...")
            fix_test_failures(test_result.failures)

        except Exception as e:
            print(f"❌ Error: {e}")

            if attempt < max_retries:
                print("Retrying with fixes...")
                apply_error_fixes(e)
            else:
                print("Max retries reached, escalating...")
                escalate_to_human(task, e)
                return None

    return None
```

---

## Best Practices

### 1. Test-Driven Development

Always write tests first or alongside implementation:

```python
# ✅ Good: Write test first
def test_create_daily_pattern():
    # Test code
    pass

def create_daily_pattern():
    # Implementation
    pass

# ❌ Bad: Implement without tests
def create_daily_pattern():
    # Implementation
    pass

# No test!
```

### 2. Small, Focused Commits

```bash
# ✅ Good: Small, focused commits
git commit -m "Add RecurringPattern model"
git commit -m "Add RecurringPatternService"
git commit -m "Add API endpoints"

# ❌ Bad: Large, unfocused commit
git commit -m "Add everything for recurring tasks"
```

### 3. Follow Conventions

```python
# ✅ Good: Follow existing conventions
class RecurringPattern(Base):  # Same as other models
    __tablename__ = "recurring_patterns"

    id = Column(Integer, primary_key=True)
    # ... consistent style

# ❌ Bad: Inconsistent conventions
class recurringPattern:  # Wrong naming
    table_name = "RecurringPatterns"  # Wrong style
```

### 4. Comprehensive Testing

```python
# ✅ Good: Test all scenarios
def test_create_daily_pattern(): pass
def test_create_weekly_pattern(): pass
def test_create_monthly_pattern(): pass
def test_invalid_recurrence_rule(): pass
def test_edge_case_leap_year(): pass

# ❌ Bad: Only happy path
def test_create_pattern(): pass
```

### 5. Error Handling

```python
# ✅ Good: Proper error handling
def create_pattern(data):
    try:
        validate_data(data)
        pattern = RecurringPattern(**data)
        db.add(pattern)
        db.commit()
        return pattern
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"DB integrity error: {e}")
        raise

# ❌ Bad: No error handling
def create_pattern(data):
    pattern = RecurringPattern(**data)
    db.add(pattern)
    db.commit()
    return pattern
```

---

## Integration with CI/CD

### Pre-commit Hooks

```bash
# .git/hooks/pre-commit

#!/bin/bash

# Run linting
echo "Running linting..."
python -m pylint backend/src/
npm run lint

# Run tests
echo "Running tests..."
pytest backend/tests/
npm test

# Check coverage
echo "Checking coverage..."
pytest --cov=backend/src backend/tests/
if [ $coverage -lt 90 ]; then
  echo "❌ Coverage below 90%"
  exit 1
fi

echo "✅ Pre-commit checks passed"
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest --cov=backend/src backend/tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Agent Script (Python Implementation)

### File: `agents/implementation_agent.py`

```python
#!/usr/bin/env python3
"""
Implementation Agent - Code Executor for Todo App Phase 5
Executes refined tasks and writes production code.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import re

@dataclass
class ImplementationResult:
    """Result of implementing a task."""
    task_id: str
    success: bool
    files_created: List[str]
    files_modified: List[str]
    tests_written: int
    tests_passing: bool
    coverage: float
    duration_hours: float
    issues: List[str]

class TaskParser:
    """Parses refined tasks."""

    def __init__(self, tasks_file: Path):
        self.tasks_file = tasks_file
        self.content = tasks_file.read_text(encoding='utf-8')

    def parse_tasks(self) -> List[Dict]:
        """Parse all tasks from file."""
        tasks = []
        pattern = r'### Task ([\d.]+): (.+?)\n\*\*Duration\*\*: ([\d.]+) hours'
        matches = re.finditer(pattern, self.content)

        for match in matches:
            task_id = match.group(1)
            title = match.group(2)
            duration = float(match.group(3))

            # Extract task details
            task_section = self._extract_task_section(task_id)

            tasks.append({
                'id': task_id,
                'title': title,
                'duration': duration,
                'description': self._extract_description(task_section),
                'steps': self._extract_steps(task_section),
                'acceptance_criteria': self._extract_acceptance_criteria(task_section),
                'test_cases': self._extract_test_cases(task_section),
                'code_references': self._extract_code_references(task_section),
                'file_paths': self._extract_file_paths(task_section),
                'dependencies': self._extract_dependencies(task_section)
            })

        return tasks

    def _extract_task_section(self, task_id: str) -> str:
        """Extract full task section."""
        pattern = rf'### Task {re.escape(task_id)}:.*?(?=###|\Z)'
        match = re.search(pattern, self.content, re.DOTALL)
        return match.group(0) if match else ""

    def _extract_description(self, section: str) -> str:
        """Extract task description."""
        match = re.search(r'\*\*Description\*\*: (.+)', section)
        return match.group(1).strip() if match else ""

    def _extract_steps(self, section: str) -> List[str]:
        """Extract implementation steps."""
        steps = []
        in_steps = False

        for line in section.split('\n'):
            if '**Steps**:' in line:
                in_steps = True
                continue
            if in_steps and line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                steps.append(line.strip()[3:])
            elif in_steps and line.startswith('**'):
                break

        return steps

    def _extract_acceptance_criteria(self, section: str) -> List[str]:
        """Extract acceptance criteria."""
        criteria = []
        in_criteria = False

        for line in section.split('\n'):
            if '**Acceptance Criteria**:' in line:
                in_criteria = True
                continue
            if in_criteria and line.strip().startswith('- [ ]'):
                criteria.append(line.strip()[6:])
            elif in_criteria and line.startswith('**'):
                break

        return criteria

    def _extract_test_cases(self, section: str) -> List[str]:
        """Extract test cases."""
        tests = []
        in_tests = False

        for line in section.split('\n'):
            if '**Test Cases**:' in line:
                in_tests = True
                continue
            if in_tests and line.strip().startswith('- '):
                tests.append(line.strip()[2:])
            elif in_tests and line.startswith('**'):
                break

        return tests

    def _extract_code_references(self, section: str) -> List[str]:
        """Extract code references."""
        refs = []
        in_refs = False

        for line in section.split('\n'):
            if '**Code References**:' in line:
                in_refs = True
                continue
            if in_refs and line.strip().startswith('- `'):
                ref = line.strip()[3:-1]  # Remove - ` and `
                refs.append(ref)
            elif in_refs and line.startswith('**'):
                break

        return refs

    def _extract_file_paths(self, section: str) -> List[str]:
        """Extract file paths."""
        paths = []
        in_paths = False

        for line in section.split('\n'):
            if '**File Paths**:' in line:
                in_paths = True
                continue
            if in_paths and line.strip().startswith('- `'):
                path = line.strip()[3:-1]
                paths.append(path)
            elif in_paths and line.startswith('**'):
                break

        return paths

    def _extract_dependencies(self, section: str) -> List[str]:
        """Extract task dependencies."""
        match = re.search(r'\*\*Dependencies\*\*: (.+)', section)
        if match:
            deps = match.group(1).strip()
            return [d.strip() for d in deps.split(',')]
        return []

class CodeGenerator:
    """Generates code from task specifications."""

    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path

    def generate_model(self, task: Dict) -> str:
        """Generate SQLAlchemy model."""
        # Simplified example - actual implementation would be more sophisticated
        template = """
from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class {model_name}(Base):
    __tablename__ = "{table_name}"

    id = Column(Integer, primary_key=True)
    # Add fields here

    def __repr__(self):
        return f"<{model_name}(id={{self.id}})>"
"""
        # Extract model name from task title
        model_name = self._extract_model_name(task['title'])
        table_name = self._to_snake_case(model_name) + 's'

        return template.format(
            model_name=model_name,
            table_name=table_name
        )

    def generate_service(self, task: Dict) -> str:
        """Generate service layer code."""
        # Simplified example
        template = """
from typing import Optional, List
from sqlalchemy.orm import Session
from ..models import {model_name}

class {model_name}Service:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> {model_name}:
        instance = {model_name}(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get(self, id: int) -> Optional[{model_name}]:
        return self.db.query({model_name}).filter({model_name}.id == id).first()

    def list(self) -> List[{model_name}]:
        return self.db.query({model_name}).all()

    def update(self, id: int, **kwargs) -> Optional[{model_name}]:
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        instance = self.get(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
"""
        model_name = self._extract_model_name(task['title'])
        return template.format(model_name=model_name)

    def _extract_model_name(self, title: str) -> str:
        """Extract model name from task title."""
        # Simple heuristic
        words = title.split()
        for word in words:
            if word[0].isupper():
                return word
        return "Model"

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

class TestGenerator:
    """Generates test files."""

    def generate_unit_tests(self, task: Dict) -> str:
        """Generate unit tests."""
        template = """
import pytest
from src.models import {model_name}

def test_create_{model_snake}():
    # Test implementation
    pass

def test_{model_snake}_validation():
    # Test validation
    pass
"""
        model_name = self._extract_model_name(task['title'])
        model_snake = self._to_snake_case(model_name)

        return template.format(
            model_name=model_name,
            model_snake=model_snake
        )

    def _extract_model_name(self, title: str) -> str:
        words = title.split()
        for word in words:
            if word[0].isupper():
                return word
        return "Model"

    def _to_snake_case(self, name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

class TestRunner:
    """Runs tests and collects results."""

    def run_pytest(self, test_dir: Path) -> Dict:
        """Run pytest and return results."""
        try:
            result = subprocess.run(
                ['pytest', str(test_dir), '--tb=short', '--cov', '--json-report'],
                capture_output=True,
                text=True,
                cwd=self.codebase_path
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'errors': str(e)
            }

class ImplementationAgent:
    """Main Implementation Agent orchestrator."""

    def __init__(self, feature_path: Path, codebase_path: Path):
        self.feature_path = feature_path
        self.codebase_path = codebase_path
        self.task_parser = TaskParser(feature_path / "tasks-refined.md")
        self.code_generator = CodeGenerator(codebase_path)
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner()

    def implement_all_tasks(self):
        """Implement all tasks."""
        tasks = self.task_parser.parse_tasks()
        results = []

        print(f"Found {len(tasks)} tasks to implement")

        for task in tasks:
            print(f"\n🔨 Implementing Task {task['id']}: {task['title']}")
            result = self.implement_task(task)
            results.append(result)

            if result.success:
                print(f"✅ Task {task['id']} completed successfully")
            else:
                print(f"❌ Task {task['id']} failed")
                break  # Stop on first failure

        # Generate report
        self._generate_report(results)

    def implement_task(self, task: Dict) -> ImplementationResult:
        """Implement a single task."""
        files_created = []
        files_modified = []
        issues = []

        try:
            # 1. Generate code
            if 'model' in task['title'].lower():
                code = self.code_generator.generate_model(task)
                # Write to file
                # files_created.append(...)

            elif 'service' in task['title'].lower():
                code = self.code_generator.generate_service(task)
                # Write to file
                # files_created.append(...)

            # 2. Generate tests
            tests = self.test_generator.generate_unit_tests(task)
            # Write tests
            # files_created.append(...)

            # 3. Run tests
            test_results = self.test_runner.run_pytest(self.codebase_path / "tests")

            return ImplementationResult(
                task_id=task['id'],
                success=test_results['success'],
                files_created=files_created,
                files_modified=files_modified,
                tests_written=len(task['test_cases']),
                tests_passing=test_results['success'],
                coverage=0.90,  # Would extract from test results
                duration_hours=task['duration'],
                issues=issues
            )

        except Exception as e:
            issues.append(str(e))
            return ImplementationResult(
                task_id=task['id'],
                success=False,
                files_created=files_created,
                files_modified=files_modified,
                tests_written=0,
                tests_passing=False,
                coverage=0.0,
                duration_hours=0.0,
                issues=issues
            )

    def _generate_report(self, results: List[ImplementationResult]):
        """Generate implementation report."""
        report = f"""# Implementation Report

## Summary

- **Total Tasks**: {len(results)}
- **Completed**: {sum(1 for r in results if r.success)}
- **Failed**: {sum(1 for r in results if not r.success)}

## Task Details

"""
        for result in results:
            report += f"""
### Task {result.task_id}
- **Status**: {'✅ Success' if result.success else '❌ Failed'}
- **Files Created**: {len(result.files_created)}
- **Tests Written**: {result.tests_written}
- **Coverage**: {result.coverage:.1%}
"""

        output_file = self.feature_path / "implementation-report.md"
        output_file.write_text(report)
        print(f"\n📄 Report saved to: {output_file}")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Implementation Agent - Execute implementation tasks")
    parser.add_argument('--feature', type=str, required=True,
                       help='Feature name (e.g., recurring-tasks)')
    parser.add_argument('--specs-dir', type=Path, default=Path('specs'),
                       help='Specs directory')
    parser.add_argument('--codebase', type=Path, default=Path('../todo_phase3'),
                       help='Codebase path')

    args = parser.parse_args()

    feature_path = args.specs_dir / args.feature

    if not feature_path.exists():
        print(f"Error: Feature path not found: {feature_path}")
        return

    if not (feature_path / "tasks-refined.md").exists():
        print(f"Error: tasks-refined.md not found. Run Tasks Agent first.")
        return

    agent = ImplementationAgent(feature_path, args.codebase)
    agent.implement_all_tasks()

    print("\n✅ Implementation complete!")

if __name__ == '__main__':
    main()
```

---

## Example Usage

```bash
# Run Implementation Agent
python agents/implementation_agent.py --feature recurring-tasks

# View implementation report
cat specs/recurring-tasks/implementation-report.md

# Run tests
cd ../todo_phase3/backend
pytest tests/

# Commit changes
git add .
git commit -m "feat: Implement recurring tasks feature"
```

---

## Constraints & Invariants

**Constraints**:
- Must pass all tests before proceeding
- Code coverage must be >90%
- Must follow project conventions
- Must include proper error handling

**Invariants**:
- All acceptance criteria must be met
- Tests must be written for all code
- Code must pass quality checks
- Changes must be committed with PHR

**Non-Goals**:
- Does NOT modify unrelated code
- Does NOT skip tests
- Does NOT commit failing code
- Does NOT implement outside specifications

---

**Last Updated**: 2026-02-02
**Maintained By**: Development Team
**Status**: Active Development
