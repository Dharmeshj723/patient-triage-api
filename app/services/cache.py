import redis.asyncio as redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=None  # Required for Upstash TLS
)

def make_cache_key(data: dict) -> str:
    # Create a unique key from patient input
    key_parts = [
        str(data.get("age", "")),
        data.get("gender", ""),
        str(data.get("fever", "")),
        str(data.get("cough", "")),
        str(data.get("fatigue", "")),
        str(data.get("difficulty_breathing", "")),
        data.get("blood_pressure", ""),
        data.get("cholesterol_level", ""),
    ]
    return "triage:" + "_".join(key_parts)

async def get_cached(key: str):
    val = await redis_client.get(key)
    return json.loads(val) if val else None

async def set_cache(key: str, value: dict, ttl: int = 3600):
    await redis_client.set(key, json.dumps(value), ex=ttl)