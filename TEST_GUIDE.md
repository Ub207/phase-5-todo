# Recurring Tasks Feature - Testing Guide

## Prerequisites

Before testing, ensure you have:
- Python 3.8+ installed
- Node.js 18+ installed
- PostgreSQL database running

## Step 1: Start the Backend Server

### Option A: Quick Start (if database already set up)

```bash
cd ../todo_phase3/backend
python -m uvicorn src.main:app --reload --port 8000
```

### Option B: Full Setup (if fresh install)

```bash
cd ../todo_phase3/backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
python -m uvicorn src.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 2: Start the Frontend Server

Open a **new terminal** and run:

```bash
cd ../todo_phase3/frontend

# Install dependencies (if needed)
npm install

# Start the development server
npm run dev
```

**Expected output**:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

## Step 3: Manual UI Testing

### 3.1 Login/Register

1. Open browser: http://localhost:3000
2. Register a new account or login
3. You should see the navbar with "Chat", "Tasks", and **"Recurring Tasks"** links

### 3.2 Create a Daily Recurring Task

1. Click **"Recurring Tasks"** in the navbar
2. Click **"Create Recurring Task"** button
3. Fill in the form:
   - **Title**: "Daily Standup"
   - **Description**: "Morning team meeting"
   - **Recurrence Type**: Daily
   - **Repeat Every**: 1 day(s)
   - **Start Date**: Tomorrow's date
   - **Timezone**: Your timezone
4. Click **"Create Pattern"**
5. ✅ You should see the pattern in the list

### 3.3 Test Weekly Recurring Task

1. Click **"Create Recurring Task"** again
2. Fill in:
   - **Title**: "Weekly Review"
   - **Recurrence Type**: Weekly
   - **Repeat Every**: 1 week(s)
   - **Repeat On**: Select Monday, Wednesday, Friday
   - **Start Date**: Next Monday
3. Click **"Create Pattern"**
4. ✅ Pattern should appear in the list

### 3.4 Test Monthly Recurring Task

1. Create one more pattern:
   - **Title**: "Monthly Report"
   - **Recurrence Type**: Monthly
   - **Day of Month**: 15
   - **Start Date**: This month or next
   - **Max Occurrences**: 12
2. Click **"Create Pattern"**
3. ✅ Pattern should appear in the list

### 3.5 View Next Occurrences

1. Click **"Show Occurrences"** on any pattern
2. ✅ You should see the next 5 occurrence dates
3. Click **"Hide Occurrences"** to collapse

### 3.6 Edit a Pattern

1. Click **"Edit"** on any pattern
2. Modify the title or description
3. Click **"Update Pattern"**
4. ✅ Changes should be saved and reflected in the list

### 3.7 Delete a Pattern

1. Click **"Delete"** on a pattern
2. Confirm the deletion (choose whether to delete instances)
3. ✅ Pattern should be removed from the list

## Step 4: API Testing (Using curl or Postman)

First, get an authentication token by logging in, then test these endpoints:

### List All Patterns
```bash
curl -X GET "http://localhost:8000/api/tasks/recurring?user_id=YOUR_USER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Pattern
```bash
curl -X POST "http://localhost:8000/api/tasks/recurring" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "title": "Test Pattern",
    "description": "API test",
    "recurrence_type": "daily",
    "recurrence_rule": {"interval": 1},
    "start_date": "2026-02-05",
    "timezone": "UTC"
  }'
```

### Calculate Next Occurrences
```bash
curl -X POST "http://localhost:8000/api/tasks/recurring/1/next-occurrences?user_id=YOUR_USER_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"count": 5}'
```

## Step 5: Run Automated E2E Tests

```bash
cd ../todo_phase5/tests

# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Make sure backend is running on http://localhost:8000

# Run the tests
pytest e2e/test_recurring_tasks.py -v --asyncio-mode=auto
```

**Expected output**: All tests should pass ✅

## Testing Checklist

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Can access /recurring-tasks page
- [ ] Can create daily recurring pattern
- [ ] Can create weekly recurring pattern (with weekday selection)
- [ ] Can create monthly recurring pattern
- [ ] Can view next 5 occurrences
- [ ] Can edit existing pattern
- [ ] Can delete pattern
- [ ] Patterns persist after page refresh
- [ ] Navigation between pages works
- [ ] All E2E tests pass

## Common Issues and Solutions

### Issue: Database connection error
**Solution**: Make sure PostgreSQL is running and DATABASE_URL is set correctly in backend/.env

### Issue: "Module not found" errors
**Solution**:
```bash
cd ../todo_phase3/backend
pip install -r requirements.txt

cd ../todo_phase3/frontend
npm install
```

### Issue: Migration errors
**Solution**:
```bash
cd ../todo_phase3/backend
alembic upgrade head
```

### Issue: Port already in use
**Solution**:
- Backend: Change port with `uvicorn src.main:app --port 8001`
- Frontend: Change port in package.json or use `PORT=3001 npm run dev`

### Issue: CORS errors
**Solution**: Check that frontend URL is in backend CORS allowed origins (should be http://localhost:3000)

## Success Criteria

✅ All manual tests completed successfully
✅ All API endpoints respond correctly
✅ All E2E tests pass
✅ UI is responsive and user-friendly
✅ Data persists across page refreshes
✅ No console errors in browser or server logs

---

**Feature**: Recurring Tasks (Phase 5)
**Status**: Ready for Testing
**Date**: 2026-02-03
