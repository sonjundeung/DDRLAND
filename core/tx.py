import time
import uuid
import json
from core.user_storage import get_redis

def make_txid(reason: str, user_id: int):
    tstr = time.strftime('%Y%m%d%H%M%S', time.localtime())
    return f"{reason}:{user_id}:{tstr}:{uuid.uuid4().hex[:8]}"

async def add_transaction(user_id: int, tx_data: dict):
    r = await get_redis()
    key = f"tx:{user_id}"
    await r.rpush(key, json.dumps(tx_data))
