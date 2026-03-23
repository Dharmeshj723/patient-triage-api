from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/")
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT
            priority,
            COUNT(*) as total,
            ROUND(AVG(confidence)::numeric, 2) as avg_confidence
        FROM triage_records
        GROUP BY priority
        ORDER BY MIN(triage_level)
    """))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]