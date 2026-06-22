import sys
import os
from pathlib import Path

# Add the parent directory (project root) to sys.path so that 'common' can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import seasons
from common.database import engine, Base
from common.config import API_TITLE, API_VERSION, API_DESCRIPTION

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seasons.router)

@app.get("/")
def root():
    return {"message": "NBA Analytics API", "docs": "/docs"}