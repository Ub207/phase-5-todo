# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, tasks

app = FastAPI(title="Todo Phase5 API", version="1.0.0")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://todo-phase3.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        from database import engine, Base
        import models
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Todo Phase5 Backend API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login"
            },
            "tasks": {
                "list": "GET /api/tasks/{user_id}",
                "create": "POST /api/tasks/{user_id}",
                "update": "PUT /api/tasks/{user_id}/{task_id}",
                "complete": "PUT /api/tasks/{user_id}/{task_id}/complete",
                "delete": "DELETE /api/tasks/{user_id}/{task_id}"
            },
            "legacy": {
                "recurring": "GET /recurring/run"
            }
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production"}

@app.get("/recurring/run")
def run_recurring_tasks():
    from recurring import process_recurring_tasks
    tasks_created = process_recurring_tasks()
    return {"status": "Recurring tasks executed", "tasks_created": tasks_created}

