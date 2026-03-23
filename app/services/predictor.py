import joblib
import numpy as np
from pathlib import Path

# Load model once when the app starts
MODEL_PATH = Path("ml/triage_model.pkl")
FEATURES_PATH = Path("ml/features.pkl")

model = joblib.load(MODEL_PATH)
FEATURES = joblib.load(FEATURES_PATH)

TRIAGE_META = {
    1: {
        "priority": "CRITICAL",
        "color": "RED",
        "action": "Immediate physician attention required. Do not wait."
    },
    2: {
        "priority": "URGENT",
        "color": "ORANGE",
        "action": "Seen within 30 minutes. Close monitoring required."
    },
    3: {
        "priority": "MODERATE",
        "color": "YELLOW",
        "action": "Stable condition. Seen within 2 hours."
    },
    4: {
        "priority": "MINOR",
        "color": "GREEN",
        "action": "Non-urgent. Can wait. Self-care may be appropriate."
    },
}

def predict_triage(
    age: int,
    gender: str,
    fever: bool,
    cough: bool,
    fatigue: bool,
    difficulty_breathing: bool,
    blood_pressure: str,
    cholesterol_level: str,
) -> dict:

    bp_map = {"low": 0, "normal": 1, "high": 2}
    chol_map = {"low": 0, "normal": 1, "high": 2}

    features = np.array([[
        age,
        1 if gender.lower() == "male" else 0,
        1 if fever else 0,
        1 if cough else 0,
        1 if fatigue else 0,
        1 if difficulty_breathing else 0,
        bp_map.get(blood_pressure.lower(), 1),
        chol_map.get(cholesterol_level.lower(), 1),
    ]])

    triage_level = int(model.predict(features)[0])
    confidence = float(model.predict_proba(features).max())
    meta = TRIAGE_META[triage_level]

    return {
        "triage_level": triage_level,
        "priority": meta["priority"],
        "color": meta["color"],
        "recommended_action": meta["action"],
        "confidence": round(confidence, 2),
    }