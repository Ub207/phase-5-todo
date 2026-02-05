from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, tasks
import re

app = FastAPI(title="Todo Phase5 API", version="1.0.0")

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


