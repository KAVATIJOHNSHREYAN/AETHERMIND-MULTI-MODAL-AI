from typing import Optional, Any
from app.config.settings import settings
from app.logging.logger import logger

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

class RedisManager:
    """Enterprise Redis Cache & Broker Connection Manager"""

    def __init__(self):
        self.client: Optional[Any] = None

    async def connect(self):
        if not REDIS_AVAILABLE:
            logger.info("redis package not installed in environment; skipping Redis connection pool.")
            return
        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5.0,
            )
            logger.info("Redis Connection Pool initialized.")
        except Exception as e:
            logger.warning(f"Redis Connection initialization warning: {str(e)}")

    async def disconnect(self):
        if self.client and hasattr(self.client, "close"):
            await self.client.close()
            logger.info("Redis Connection closed.")

    async def health_check(self) -> dict:
        if not REDIS_AVAILABLE:
            return {
                "status": "degraded",
                "cache": "redis",
                "connected": False,
                "message": "redis package not installed in environment"
            }
        if not self.client:
            return {"status": "unhealthy", "cache": "redis", "connected": False, "details": "Client not initialized"}
        try:
            pong = await self.client.ping()
            if pong:
                return {"status": "healthy", "cache": "redis", "connected": True}
        except Exception as e:
            return {"status": "degraded", "cache": "redis", "connected": False, "error": str(e)}
        return {"status": "unhealthy", "cache": "redis", "connected": False}

redis_manager = RedisManager()
