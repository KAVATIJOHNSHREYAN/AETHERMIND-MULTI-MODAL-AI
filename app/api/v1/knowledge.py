"""
AetherMind Multimodal AI — Knowledge Base API (Phase 8)
Supports Knowledge Base Collections, Ingesting PDF/Word/Markdown/Text Documents, Chunk Embedding, Tagging, and Management.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File as FastAPIFile, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.memory.knowledge_service import knowledge_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []


@router.post("/collections", response_model=APIResponse[dict])
async def create_knowledge_collection(
    req: CreateCollectionRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new Knowledge Base Collection for vector RAG documents."""
    res = await knowledge_service.create_collection(
        db=db,
        user_id="default-user-id",
        name=req.name,
        description=req.description,
        tags=req.tags
    )
    return APIResponse(success=True, data=res, message=f"Knowledge Collection '{req.name}' created")


@router.get("/collections", response_model=APIResponse[List[dict]])
async def list_knowledge_collections(db: AsyncSession = Depends(get_async_db)):
    """Retrieve all Knowledge Base Collections."""
    cols = await knowledge_service.list_collections(db=db, user_id="default-user-id")
    return APIResponse(success=True, data=cols, message="Knowledge Collections loaded")


@router.post("/ingest", response_model=APIResponse[dict])
async def ingest_knowledge_document(
    file: UploadFile = FastAPIFile(...),
    collection_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Ingest document (PDF, Word, Markdown, Text) into Knowledge Base with automatic chunking and vector embedding."""
    filename = file.filename or "knowledge_doc.txt"
    content_bytes = await file.read()

    tag_list = [t.strip() for t in tags.split(",")] if tags else ["general"]

    res = await knowledge_service.ingest_document(
        db=db,
        user_id="default-user-id",
        collection_id=collection_id or "default_collection",
        filename=filename,
        content_bytes=content_bytes,
        tags=tag_list
    )

    return APIResponse(success=True, data=res, message=f"Ingested '{filename}' into Knowledge Base ({res.get('chunk_count')} chunks indexed)")


@router.get("/documents", response_model=APIResponse[List[dict]])
async def list_knowledge_documents(
    collection_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve ingested Knowledge Base documents."""
    docs = await knowledge_service.list_documents(db=db, collection_id=collection_id)
    return APIResponse(success=True, data=docs, message="Knowledge Documents loaded")


@router.delete("/documents/{doc_id}", response_model=APIResponse[dict])
async def delete_knowledge_document(doc_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete a document from Knowledge Base."""
    success = await knowledge_service.delete_document(db=db, doc_id=doc_id)
    return APIResponse(success=success, message=f"Knowledge Document {doc_id} removed", data={"id": doc_id})
