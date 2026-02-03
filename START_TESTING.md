# Quick Start - Testing Recurring Tasks Feature

## Step 1: Start the Backend (Terminal 1)

**Option A: Using the startup script**
```bash
.\start_backend.bat
```

**Option B: Manual start**
```bash
cd ..\todo_phase3\backend
python -m uvicorn src.main:app --reload --port 8000
```

**Wait for**: `Application startup complete.`

**Verify**: Open http://localhost:8000/docs - you should see the API documentation

---

## Step 2: Start the Frontend (Terminal 2)

Open a **NEW terminal window** and run:

**Option A: Using the startup script**
```bash
.\start_frontend.bat
```

**Option B: Manual start**
```bash
cd ..\todo_phase3\frontend
npm run dev
```

**Wait for**: `Ready in X.Xs`

**Verify**: Frontend is at http://localhost:3000

---

## Step 3: Test the Feature

### 3.1 Access the App
1. Open browser: **http://localhost:3000**
2. Register/Login with any credentials
3. Click **"Recurring Tasks"** in the navbar

### 3.2 Quick Test (5 minutes)

**Create a Daily Pattern:**
- Title: "Morning Standup"
- Type: Daily
- Interval: 1 day
- Start: Tomorrow
- Click "Create Pattern"

**Create a Weekly Pattern:**
- Title: "Team Meeting"
- Type: Weekly
- Select: Monday, Wednesday
- Start: Next Monday
- Click "Create Pattern"

**View Occurrences:**
- Click "Show Occurrences" on any pattern
- You should see the next 5 dates

**Edit a Pattern:**
- Click "Edit" on a pattern
- Change the title
- Click "Update Pattern"

**Delete a Pattern:**
- Click "Delete" on a pattern
- Confirm deletion

### 3.3 Success Indicators
✅ All patterns appear in the list
✅ Next occurrences are calculated correctly
✅ Edit updates the pattern
✅ Delete removes the pattern
✅ Data persists after page refresh

---

## Step 4: Run Automated Tests (Optional)

In a **third terminal**:

```bash
cd tests
pip install pytest pytest-asyncio httpx
pytest e2e/test_recurring_tasks.py -v --asyncio-mode=auto
```

All 13 tests should pass ✅

---

## Troubleshooting

### Backend won't start
1. Check PostgreSQL is running
2. Check `.env` file exists in `backend/` with correct DATABASE_URL
3. Run migrations: `cd backend && alembic upgrade head`

### Frontend won't start
1. Install dependencies: `cd frontend && npm install`
2. Check Node.js version: `node --version` (should be 18+)

### Can't see Recurring Tasks page
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check CORS settings allow localhost:3000

### Database errors
```bash
cd ..\todo_phase3\backend
alembic upgrade head
```

---

## Files Created for Testing

- `start_backend.bat` - Quick backend startup
- `start_frontend.bat` - Quick frontend startup
- `TEST_GUIDE.md` - Detailed testing guide
- `quick_test.py` - Automated backend verification

---

## What You're Testing

### Backend APIs (8 endpoints)
- POST /api/tasks/recurring - Create pattern
- GET /api/tasks/recurring - List patterns
- GET /api/tasks/recurring/{id} - Get pattern
- PUT /api/tasks/recurring/{id} - Update pattern
- DELETE /api/tasks/recurring/{id} - Delete pattern
- POST /api/tasks/recurring/{id}/next-occurrences
- POST /api/tasks/recurring/{id}/skip
- POST /api/tasks/recurring/{id}/postpone

### Frontend Components
- RecurringTaskForm - Create/edit interface
- RecurringTaskList - Display patterns
- /recurring-tasks page - Full UI

### Features
- ✅ Daily recurring patterns
- ✅ Weekly recurring patterns (with day selection)
- ✅ Monthly recurring patterns
- ✅ Custom intervals
- ✅ Next occurrence calculation
- ✅ Pattern CRUD operations
- ✅ Timezone support

---

**Ready to start testing? Run `.\start_backend.bat` in one terminal and `.\start_frontend.bat` in another!**
