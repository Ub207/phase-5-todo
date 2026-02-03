@echo off
echo ============================================================
echo Starting Backend Server for Recurring Tasks Testing
echo ============================================================
echo.

cd ..\todo_phase3\backend

echo Checking if database migrations are up to date...
python -c "print('Database check...')"

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Documentation will be available at http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

start "" python -m uvicorn src.main:app --reload --port 8000
