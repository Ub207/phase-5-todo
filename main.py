from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import recurring task logic
from recurring import process_recurring_tasks

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todo-phase3.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production"}

# Recurring tasks endpoint
@app.get("/recurring/run")
def run_recurring_tasks():
    tasks_created = process_recurring_tasks()
    return {"status": "Recurring tasks executed", "tasks_created": tasks_created}
