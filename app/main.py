from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.db.database import engine, Base
from app.routes import triage, history, stats
from app.services.cache import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS triage_records (
                id TEXT PRIMARY KEY,
                age INTEGER,
                gender TEXT,
                fever BOOLEAN,
                cough BOOLEAN,
                fatigue BOOLEAN,
                difficulty_breathing BOOLEAN,
                blood_pressure TEXT,
                cholesterol_level TEXT,
                triage_level INTEGER,
                priority TEXT,
                confidence FLOAT,
                created_at TIMESTAMP
            )
        """))
    print("✅ Database tables ready")
    yield
    await engine.dispose()
    await redis_client.aclose()

app = FastAPI(
    title="Patient Triage API",
    description="Real-time patient triage prediction using ML",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router)
app.include_router(history.router)
app.include_router(stats.router)

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "model": "loaded",
        "version": "1.0.0"
    }