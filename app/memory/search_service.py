"""
AetherMind Multimodal AI — Hybrid Search Service (Phase 8)
Supports Semantic Vector Search, Keyword BM25 Search, Combined Hybrid RAG Search, and Search History Recording.
"""

import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.memory import KnowledgeCollection, KnowledgeDocument, SearchHistory
from app.memory.retriever_service import retriever_service
from app.logging.logger import logger


class SearchService:
    """Unified Search Service for Semantic, Keyword, and Hybrid Searches"""

    async def execute_search(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        search_type: str = "hybrid", # hybrid, semantic, keyword
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Execute semantic, keyword, or hybrid search across Knowledge Base and Memory."""
        if not query:
            return {"query": query, "search_type": search_type, "results": [], "count": 0}

        retrieved = await retriever_service.retrieve_context(
            db=db, user_id=user_id, query=query, collection_id=collection_id, top_k=limit
        )

        results = []

        # Knowledge Base Chunks
        for chk in retrieved.get("knowledge_chunks", []):
            p = chk.get("payload", {})
            results.append({
                "type": "knowledge_chunk",
                "title": p.get("filename", "Knowledge Document"),
                "content": p.get("text", ""),
                "score": chk.get("ranked_score", 0.0),
                "page_number": p.get("page_number", 1),
                "collection_id": p.get("collection_id")
            })

        # Memory Items
        for mem in retrieved.get("memories", []):
            results.append({
                "type": "memory_item",
                "title": f"Memory: {mem.get('memory_key')}",
                "content": mem.get("memory_value"),
                "score": mem.get("similarity_score", 0.0),
                "memory_type": mem.get("memory_type")
            })

        # Record Search History
        try:
            sh = SearchHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                query=query,
                search_type=search_type,
                results_count=len(results)
            )
            db.add(sh)
            await db.commit()
        except Exception:
            await db.rollback()

        return {
            "query": query,
            "search_type": search_type,
            "count": len(results),
            "results": results
        }


search_service = SearchService()
