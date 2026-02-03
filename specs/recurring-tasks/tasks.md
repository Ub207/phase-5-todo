# Tasks: recurring-tasks

**Feature**: recurring-tasks
**Priority**: high
**Complexity**: 9/10

---

## Phase 1: Setup

- [X] T001 Configure Dapr pubsub component [P] Path: `backend/dapr/pubsub.yaml`
- [X] T002 Configure Dapr statestore component [P] Path: `backend/dapr/statestore.yaml`

---

## Phase 2: Foundational

- [X] T003 Create Database Schema [US1] Path: `backend/src/models/recurring_pattern.py`
- [X] T004 Create Alembic Migration [US1] Path: `backend/alembic/versions/002_add_recurring_tasks.py`

---

## Phase 3: User Story 1 (US1) - Recurring Tasks Backend

- [X] T005 [US1] Create Recurring Pattern Models Path: `backend/src/models/recurring_pattern.py`
- [X] T006 [US1] Create Recurring Pattern Service Layer Path: `backend/src/services/recurring_pattern_service.py` (Depends on T005)
- [X] T007 [US1] Create Backend API Endpoints Path: `backend/src/api/recurring.py` (Depends on T006)

---

## Phase 4: User Story 2 (US2) - Recurring Tasks Frontend

- [X] T008 [US2] Create TaskForm Component Path: `frontend/components/RecurringTaskForm.tsx`
- [X] T009 [US2] Create TaskList Component Path: `frontend/components/RecurringTaskList.tsx` (Depends on T008)

---

## Phase 5: Polish & End-to-End Testing

- [X] T010 End-to-End Tests [P] Path: `tests/e2e/test_recurring_tasks.py` (Depends on T001-T009)

