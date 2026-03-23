from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TriageRequest(BaseModel):
    age: int = Field(..., ge=0, le=120, example=45)
    gender: str = Field(..., pattern="^(male|female|other)$", example="male")
    fever: bool = Field(..., example=True)
    cough: bool = Field(..., example=False)
    fatigue: bool = Field(..., example=True)
    difficulty_breathing: bool = Field(..., example=True)
    blood_pressure: str = Field(..., pattern="^(low|normal|high)$", example="high")
    cholesterol_level: str = Field(..., pattern="^(low|normal|high)$", example="normal")

class TriageResponse(BaseModel):
    triage_level: int
    priority: str
    color: str
    recommended_action: str
    confidence: float
    record_id: str
    timestamp: datetime
    cached: bool = False

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database: str
    cache: str