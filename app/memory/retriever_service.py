"""
AetherMind Multimodal AI — RAG Context Retriever Service (Phase 8)
Retrieves semantic knowledge chunks and long-term memory points, reranks them, and assembles structured system prompt context.
"""

import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.memory import KnowledgeCollection, RetrievalHistory
from app.vector.qdrant_client import qdrant_manager
from app.memory.embedding_service import embedding_service
from app.memory.memory_service import memory_service
from app.memory.ranking_service import ranking_service
from app.logging.logger import logger


class RetrieverService:
    """RAG Retriever & Prompt Context Assembly Engine"""

    async def retrieve_context(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        collection_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Perform full RAG retrieval pipeline across Knowledge Base and Long-Term Memory."""
        if not query:
            return {"context_block": "", "knowledge_chunks": [], "memories": []}

        # 1. Retrieve Long-Term Memories
        memories = await memory_service.retrieve_relevant_memories(
            db=db, user_id=user_id, query=query, limit=3
        )

        # 2. Retrieve Knowledge Base Chunks
        query_vector = await embedding_service.generate_embedding(query)
        knowledge_chunks = []

        # Find target Qdrant collection name
        qdrant_cols = []
        if collection_id:
            c_res = await db.execute(select(KnowledgeCollection).where(KnowledgeCollection.id == collection_id))
            col_rec = c_res.scalar_one_or_none()
            if col_rec:
                qdrant_cols.append(col_rec.qdrant_collection_name)
        else:
            # Query all user collections
            c_res = await db.execute(select(KnowledgeCollection).where(KnowledgeCollection.user_id == user_id))
            cols = c_res.scalars().all()
            for c in cols:
                qdrant_cols.append(c.qdrant_collection_name)

        # Perform vector similarity search across collections
        raw_chunks = []
        for q_col in qdrant_cols:
            matches = await qdrant_manager.search_similarity(
                collection_name=q_col,
                query_vector=query_vector,
                limit=top_k
            )
            raw_chunks.extend(matches)

        # 3. Hybrid Reranking
        ranked_chunks = ranking_service.rank_chunks(raw_chunks, query)
        top_chunks = ranked_chunks[:top_k]

        # 4. Assemble Structured RAG Context Prompt Block
        context_lines = []

        if memories:
            context_lines.append("=== RETRIEVED LONG-TERM MEMORIES ===")
            for m in memories:
                context_lines.append(f"• [{m.get('memory_type', 'persistent').upper()}] {m.get('memory_key')}: {m.get('memory_value')}")
            context_lines.append("")

        if top_chunks:
            context_lines.append("=== RETRIEVED KNOWLEDGE BASE CONTEXT ===")
            for idx, chk in enumerate(top_chunks, 1):
                p = chk.get("payload", {})
                filename = p.get("filename", "Knowledge Document")
                score = chk.get("ranked_score", 0.0)
                text = p.get("text", "")
                context_lines.append(f"Chunk #{idx} [Doc: {filename} | Relevance: {score}]:\n{text}\n")

        context_block = "\n".join(context_lines)

        # Record Retrieval History
        top_score = top_chunks[0].get("ranked_score", 0.0) if top_chunks else 0.0
        try:
            h_rec = RetrievalHistory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                query=query,
                retrieved_chunks_count=len(top_chunks),
                top_similarity_score=top_score,
                retrieved_payload=[{"doc": c.get("payload", {}).get("filename"), "score": c.get("ranked_score")} for c in top_chunks]
            )
            db.add(h_rec)
            await db.commit()
        except Exception:
            await db.rollback()

        return {
            "query": query,
            "context_block": context_block,
            "knowledge_chunks": top_chunks,
            "memories": memories,
            "top_similarity_score": top_score
        }


retriever_service = RetrieverService()
