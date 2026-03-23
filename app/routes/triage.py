from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import uuid

from app.models.schema import TriageRequest, TriageResponse
from app.services.predictor import predict_triage
from app.services.cache import make_cache_key, get_cached, set_cache
from app.db.database import get_db

router = APIRouter(prefix="/triage", tags=["Triage"])

@router.post("/", response_model=TriageResponse)
async def create_triage(request: TriageRequest, db: AsyncSession = Depends(get_db)):

    # Check cache first
    cache_key = make_cache_key(request.model_dump())
    cached = await get_cached(cache_key)

    if cached:
        cached["cached"] = True
        cached["record_id"] = str(uuid.uuid4())
        cached["timestamp"] = datetime.utcnow()
        return cached

    # Run ML prediction
    result = predict_triage(
        age=request.age,
        gender=request.gender,
        fever=request.fever,
        cough=request.cough,
        fatigue=request.fatigue,
        difficulty_breathing=request.difficulty_breathing,
        blood_pressure=request.blood_pressure,
        cholesterol_level=request.cholesterol_level,
    )

    # Save to DB
    record_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO triage_records
        (id, age, gender, fever, cough, fatigue, difficulty_breathing,
         blood_pressure, cholesterol_level, triage_level, priority, confidence, created_at)
        VALUES
        (:id, :age, :gender, :fever, :cough, :fatigue, :difficulty_breathing,
         :blood_pressure, :cholesterol_level, :triage_level, :priority, :confidence, :created_at)
    """), {
        "id": record_id,
        "age": request.age,
        "gender": request.gender,
        "fever": request.fever,
        "cough": request.cough,
        "fatigue": request.fatigue,
        "difficulty_breathing": request.difficulty_breathing,
        "blood_pressure": request.blood_pressure,
        "cholesterol_level": request.cholesterol_level,
        "triage_level": result["triage_level"],
        "priority": result["priority"],
        "confidence": result["confidence"],
        "created_at": datetime.utcnow(),
    })
    await db.commit()

    # Cache result
    await set_cache(cache_key, result)

    return TriageResponse(
        **result,
        record_id=record_id,
        timestamp=datetime.utcnow(),
        cached=False,
    )