# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from recurring import process_recurring_tasks

app = FastAPI()

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

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": "production"}

@app.get("/recurring/run")
def run_recurring_tasks():
    tasks_created = process_recurring_tasks()
    return {"status": "Recurring tasks executed", "tasks_created": tasks_created}

