import hashlib
import secrets
import json
import aioredis
from core.config import REDIS_URL

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

async def get_user(uid: int):
    r = await get_redis()
    data = await r.get(f"user:{uid}")
    return json.loads(data) if data else None

async def set_user(uid: int, user: dict):
    r = await get_redis()
    await r.set(f"user:{uid}", json.dumps(user))

def generate_recovery_code(blocks=4, block_size=4):
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return '-'.join(
        ''.join(secrets.choice(chars) for _ in range(block_size))
        for _ in range(blocks)
    )

def hash_recovery_code(code: str):
    return hashlib.sha256(code.replace("-", "").replace(" ", "").strip().encode()).hexdigest()
