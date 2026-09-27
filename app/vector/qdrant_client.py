from typing import Optional
from app.config.settings import settings
from app.logging.logger import logger

try:
    from qdrant_client import AsyncQdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    AsyncQdrantClient = None
    QDRANT_AVAILABLE = False

class QdrantManager:
    """Enterprise Qdrant Vector Database Infrastructure Manager"""

    def __init__(self):
        self.client: Optional[Any] = None

    async def connect(self):
        if not QDRANT_AVAILABLE:
            logger.info("Qdrant client package not installed in environment; skipping vector DB connection pool.")
            return
        try:
            self.client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=5.0,
            )
            logger.info("Qdrant Vector DB Client initialized.")
        except Exception as e:
            logger.warning(f"Qdrant Client initialization warning: {str(e)}")

    async def disconnect(self):
        if self.client and hasattr(self.client, "close"):
            await self.client.close()
            logger.info("Qdrant Vector DB Client disconnected.")

    async def health_check(self) -> dict:
        if not QDRANT_AVAILABLE:
            return {
                "status": "degraded",
                "vector_db": "qdrant",
                "connected": False,
                "message": "qdrant-client package not installed in environment"
            }
        if not self.client:
            return {"status": "unhealthy", "vector_db": "qdrant", "connected": False, "details": "Client not initialized"}
        try:
            collections = await self.client.get_collections()
            return {
                "status": "healthy",
                "vector_db": "qdrant",
                "connected": True,
                "collections_count": len(collections.collections)
            }
        except Exception as e:
            return {"status": "degraded", "vector_db": "qdrant", "connected": False, "error": str(e)}

qdrant_manager = QdrantManager()
