from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/")
async def get_history(
    limit: int = Query(default=10, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(text("""
        SELECT id, age, gender, triage_level, priority,
               confidence, created_at
        FROM triage_records
        ORDER BY created_at DESC
        LIMIT :limit
    """), {"limit": limit})

    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]