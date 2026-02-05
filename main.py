from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, tasks
from database import engine, Base
from models import User, Task, RecurringRule
import re

app = FastAPI(title="Todo Phase5 API", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

# CORS configuration - allow frontend domains
origins = [
    "http://localhost:3000",
    "https://frontend-hazel-gamma-xtb0q17d6f.vercel.app",
]

# Allow all Vercel preview deployments
allow_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"status": "ok"}


