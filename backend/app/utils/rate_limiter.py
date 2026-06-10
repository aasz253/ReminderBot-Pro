from typing import Optional

from redis import asyncio as aioredis

from app.core.config import settings


class RateLimiter:
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis = redis_client

    async def is_rate_limited(
        self, key: str, max_requests: int = 60, window_seconds: int = 60
    ) -> bool:
        if not settings.RATE_LIMIT_ENABLED:
            return False
        if not self.redis:
            return False

        try:
            current = await self.redis.get(key)
            if current is not None and int(current) >= max_requests:
                return True
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            await pipe.execute()
            return False
        except Exception:
            return False

    async def get_remaining(self, key: str, max_requests: int = 60) -> int:
        if not self.redis:
            return max_requests
        try:
            current = await self.redis.get(key)
            if current is None:
                return max_requests
            return max(0, max_requests - int(current))
        except Exception:
            return max_requests

    async def reset(self, key: str) -> None:
        if self.redis:
            await self.redis.delete(key)
