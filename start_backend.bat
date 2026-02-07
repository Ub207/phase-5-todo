@echo off
echo ============================================================
echo Starting Todo Phase 5 Backend Server
echo ============================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server on http://localhost:8000
echo API Documentation will be available at http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

uvicorn main:app --reload --port 8000
