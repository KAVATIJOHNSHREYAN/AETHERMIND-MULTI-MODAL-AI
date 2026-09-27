"""
AetherMind Multimodal AI — Knowledge Base Service (Phase 8)
Supports Knowledge Collections, Document Ingestion (PDF, DOCX, MD, TXT), Chunk Embedding Pipeline, Tagging, Listing, and Deletion.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from app.models.memory import KnowledgeCollection, KnowledgeDocument, EmbeddingReference
from app.documents.rag_engine import document_engine
from app.vector.qdrant_client import qdrant_manager
from app.memory.embedding_service import embedding_service
from app.logging.logger import logger


class KnowledgeService:
    """Knowledge Base System Manager for Enterprise Knowledge Collections & RAG Chunks Ingestion"""

    async def create_collection(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create new Knowledge Base Collection and register Qdrant Vector Collection."""
        col_id = str(uuid.uuid4())
        qdrant_col_name = f"kb_col_{col_id.replace('-', '_')}"

        # Ensure Qdrant Vector Collection exists
        await qdrant_manager.ensure_collection(collection_name=qdrant_col_name, vector_size=1536)

        rec = KnowledgeCollection(
            id=col_id,
            user_id=user_id,
            name=name,
            description=description or "",
            tags=tags or [],
            qdrant_collection_name=qdrant_col_name,
            doc_count=0
        )

        try:
            db.add(rec)
            await db.commit()
            await db.refresh(rec)
        except Exception as e:
            logger.warning(f"DB Collection creation warning: {e}")
            await db.rollback()

        return {
            "id": col_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "doc_count": 0,
            "qdrant_collection_name": qdrant_col_name,
            "created_at": rec.created_at.isoformat() if rec.created_at else datetime.utcnow().isoformat()
        }

    async def ingest_document(
        self,
        db: AsyncSession,
        user_id: str,
        collection_id: str,
        filename: str,
        content_bytes: bytes,
        tags: Optional[List[str]] = None,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ingest document into Knowledge Collection, extract text, chunk, embed, and index into Qdrant."""
        # 1. Check if collection exists, else create default
        col_res = await db.execute(select(KnowledgeCollection).where(KnowledgeCollection.id == collection_id))
        collection = col_res.scalar_one_or_none()

        if not collection:
            col_dict = await self.create_collection(db, user_id, "Default Knowledge Collection")
            collection_id = col_dict["id"]
            qdrant_col_name = col_dict["qdrant_collection_name"]
        else:
            qdrant_col_name = collection.qdrant_collection_name

        # 2. Parse document text & extract RAG chunks architecture
        parsed = await document_engine.parse_document(filename, content_bytes)
        extracted_text = parsed.get("extracted_text", "")
        chunks = parsed.get("chunks", [])

        if not chunks and extracted_text:
            chunks = [{"chunk_id": 0, "page_number": 1, "text": extracted_text[:800]}]

        doc_id = str(uuid.uuid4())
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ".txt"

        # 3. Generate embeddings & index chunks in Qdrant
        points_to_upsert = []
        for idx, chunk in enumerate(chunks):
            chunk_text = chunk.get("text", "")
            if not chunk_text:
                continue

            vector = await embedding_service.generate_embedding(chunk_text)
            point_id = f"{doc_id[:8]}_{idx}"

            payload = {
                "doc_id": doc_id,
                "collection_id": collection_id,
                "user_id": user_id,
                "filename": filename,
                "chunk_id": chunk.get("chunk_id", idx),
                "page_number": chunk.get("page_number", 1),
                "text": chunk_text,
                "tags": tags or []
            }

            points_to_upsert.append({
                "id": point_id,
                "vector": vector,
                "payload": payload
            })

            # Record embedding reference
            db.add(EmbeddingReference(
                id=str(uuid.uuid4()),
                user_id=user_id,
                entity_type="document_chunk",
                entity_id=doc_id,
                provider_name="openai",
                model_name="text-embedding-3-small",
                dimensions=1536,
                qdrant_point_id=point_id
            ))

        if points_to_upsert:
            await qdrant_manager.upsert_points(collection_name=qdrant_col_name, points=points_to_upsert)

        # 4. Save KnowledgeDocument DB Record
        doc_rec = KnowledgeDocument(
            id=doc_id,
            collection_id=collection_id,
            user_id=user_id,
            file_id=file_id,
            title=filename,
            file_type=ext.replace(".", ""),
            content=extracted_text,
            chunk_count=len(chunks),
            tags=tags or [],
            doc_metadata=parsed.get("metadata", {})
        )
        db.add(doc_rec)

        # Update collection document count
        await db.execute(
            update(KnowledgeCollection)
            .where(KnowledgeCollection.id == collection_id)
            .values(doc_count=KnowledgeCollection.doc_count + 1)
        )

        try:
            await db.commit()
            await db.refresh(doc_rec)
        except Exception as e:
            logger.warning(f"Error saving Knowledge Document: {e}")
            await db.rollback()

        return {
            "id": doc_id,
            "collection_id": collection_id,
            "title": filename,
            "file_type": ext.replace(".", ""),
            "chunk_count": len(chunks),
            "tags": tags or [],
            "created_at": doc_rec.created_at.isoformat() if doc_rec.created_at else datetime.utcnow().isoformat()
        }

    async def list_collections(self, db: AsyncSession, user_id: str = "default-user-id") -> List[Dict[str, Any]]:
        """List all Knowledge Base Collections for user."""
        try:
            q = select(KnowledgeCollection).where(KnowledgeCollection.user_id == user_id).order_by(KnowledgeCollection.created_at.desc())
            res = await db.execute(q)
            cols = res.scalars().all()
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "tags": c.tags or [],
                    "doc_count": c.doc_count,
                    "qdrant_collection_name": c.qdrant_collection_name,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in cols
            ]
        except Exception as e:
            logger.warning(f"Error listing collections: {e}")
            return []

    async def list_documents(self, db: AsyncSession, collection_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List documents in Knowledge Base."""
        try:
            q = select(KnowledgeDocument)
            if collection_id:
                q = q.where(KnowledgeDocument.collection_id == collection_id)
            q = q.order_by(KnowledgeDocument.created_at.desc())
            res = await db.execute(q)
            docs = res.scalars().all()
            return [
                {
                    "id": d.id,
                    "collection_id": d.collection_id,
                    "title": d.title,
                    "file_type": d.file_type,
                    "chunk_count": d.chunk_count,
                    "tags": d.tags or [],
                    "snippet": d.content[:200] if d.content else "",
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in docs
            ]
        except Exception as e:
            logger.warning(f"Error listing documents: {e}")
            return []

    async def delete_document(self, db: AsyncSession, doc_id: str) -> bool:
        """Delete Knowledge document from database."""
        try:
            res = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id))
            doc = res.scalar_one_or_none()
            if doc:
                await db.delete(doc)
                await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False


knowledge_service = KnowledgeService()
