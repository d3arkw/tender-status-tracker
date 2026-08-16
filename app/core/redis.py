import json
from redis.asyncio import Redis
from app.core.config import get_settings

CACHE_TTL = 300
redis_client = Redis.from_url(get_settings().redis_url, decode_responses=True)


def _key(tender_id: int) -> str:
    return f"tender:{tender_id}"


async def get_tender(tender_id: int) -> dict | None:
    data = await redis_client.get(_key(tender_id))
    if data is None:
        return None
    return json.loads(data)


async def set_tender(tender_id: int, data: dict) -> None:
    await redis_client.set(_key(tender_id), json.dumps(data), ex=CACHE_TTL)


async def invalidate_tender(tender_id: int) -> None:
    await redis_client.delete(_key(tender_id))
