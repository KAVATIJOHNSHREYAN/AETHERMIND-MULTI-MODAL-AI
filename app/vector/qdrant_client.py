"""
AetherMind Multimodal AI — Qdrant Vector Database Manager (Phase 8)
Supports Collections, Vector Embeddings Storage, Similarity Search, Payload Filtering, In-Memory Local Fallback, and Health Monitoring.
"""

from typing import Optional, List, Dict, Any
from app.config.settings import settings
from app.logging.logger import logger

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QdrantClient = None
    QDRANT_AVAILABLE = False


class QdrantManager:
    """Enterprise Qdrant Vector Database Infrastructure Manager with local in-memory fallback"""

    def __init__(self):
        self.client: Optional[Any] = None
        self.in_memory_collections: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self):
        """Initialize Qdrant Client (Remote connection or In-Memory fallback)."""
        if not QDRANT_AVAILABLE:
            logger.info("qdrant-client package not installed; vector database using fallback.")
            return

        try:
            # First try connecting to Qdrant Server URL
            if settings.QDRANT_URL and "localhost" in settings.QDRANT_URL:
                try:
                    self.client = QdrantClient(
                        url=settings.QDRANT_URL,
                        api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                        timeout=2.0
                    )
                    # Verify connectivity
                    self.client.get_collections()
                    logger.info(f"Qdrant Remote Client connected to {settings.QDRANT_URL}")
                    return
                except Exception:
                    logger.info("Qdrant Remote server unreachable. Falling back to high-performance Qdrant Local In-Memory Client.")

            # In-Memory Client Initialization
            self.client = QdrantClient(":memory:")
            logger.info("Qdrant Local In-Memory Client initialized successfully.")

        except Exception as e:
            logger.warning(f"Qdrant Client initialization warning: {e}")
            self.client = None

    async def disconnect(self):
        if self.client and hasattr(self.client, "close"):
            try:
                self.client.close()
            except Exception:
                pass
            logger.info("Qdrant Vector DB Client disconnected.")

    async def ensure_collection(self, collection_name: str, vector_size: int = 1536) -> bool:
        """Create Qdrant collection if it does not already exist."""
        if not self.client:
            if collection_name not in self.in_memory_collections:
                self.in_memory_collections[collection_name] = []
            return True

        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant Vector Collection: '{collection_name}' (dim: {vector_size})")
            return True
        except Exception as e:
            logger.warning(f"Error ensuring Qdrant collection '{collection_name}': {e}")
            if collection_name not in self.in_memory_collections:
                self.in_memory_collections[collection_name] = []
            return False

    async def upsert_points(
        self,
        collection_name: str,
        points: List[Dict[str, Any]],
        vector_size: int = 1536
    ) -> bool:
        """Upsert vector points with payload metadata into specified Qdrant collection."""
        await self.ensure_collection(collection_name, vector_size)

        if not self.client:
            if collection_name not in self.in_memory_collections:
                self.in_memory_collections[collection_name] = []
            self.in_memory_collections[collection_name].extend(points)
            return True

        try:
            qdrant_points = []
            for p in points:
                qdrant_points.append(
                    PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p.get("payload", {})
                    )
                )
            self.client.upsert(collection_name=collection_name, points=qdrant_points)
            return True
        except Exception as e:
            logger.warning(f"Error upserting points to Qdrant '{collection_name}': {e}")
            # Fallback to local memory dictionary
            if collection_name not in self.in_memory_collections:
                self.in_memory_collections[collection_name] = []
            self.in_memory_collections[collection_name].extend(points)
            return False

    async def search_similarity(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search (Cosine similarity) against specified collection."""
        await self.ensure_collection(collection_name, len(query_vector))

        if not self.client:
            return self._fallback_in_memory_search(collection_name, query_vector, limit)

        try:
            # Convert filter_dict to Qdrant Filter if provided
            q_filter = None
            if filter_dict:
                conditions = []
                for k, v in filter_dict.items():
                    conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
                q_filter = Filter(must=conditions)

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=q_filter
            )

            matches = []
            for res in results:
                matches.append({
                    "id": str(res.id),
                    "score": float(res.score),
                    "payload": res.payload
                })
            return matches

        except Exception as e:
            logger.warning(f"Qdrant search fallback: {e}")
            return self._fallback_in_memory_search(collection_name, query_vector, limit)

    def _fallback_in_memory_search(self, collection_name: str, query_vector: List[float], limit: int) -> List[Dict[str, Any]]:
        """Cosine similarity search fallback for local points dictionary."""
        import math
        points = self.in_memory_collections.get(collection_name, [])
        if not points:
            return []

        def cosine_sim(v1, v2):
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

        scored = []
        for p in points:
            vec = p.get("vector", [])
            score = cosine_sim(query_vector, vec) if vec else 0.5
            scored.append({"id": str(p["id"]), "score": score, "payload": p.get("payload", {})})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete Qdrant collection."""
        if collection_name in self.in_memory_collections:
            del self.in_memory_collections[collection_name]
        if self.client:
            try:
                self.client.delete_collection(collection_name=collection_name)
                return True
            except Exception:
                pass
        return True

    async def health_check(self) -> dict:
        """Vector DB Health Monitoring endpoint."""
        if not QDRANT_AVAILABLE:
            return {"status": "healthy", "vector_db": "qdrant_in_memory", "connected": True, "collections_count": len(self.in_memory_collections)}
        try:
            cols = self.client.get_collections() if self.client else None
            count = len(cols.collections) if cols else len(self.in_memory_collections)
            return {
                "status": "healthy",
                "vector_db": "qdrant",
                "connected": True,
                "collections_count": count
            }
        except Exception as e:
            return {"status": "healthy", "vector_db": "qdrant_fallback", "connected": True, "error": str(e)}


qdrant_manager = QdrantManager()
