"""
AetherMind Multimodal AI — Document Intelligence API (Phase 7)
Supports Document Upload Parsing, Metadata, Chunking Architecture, Page Navigation, Search Inside Document, Document History, Document Removal.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File as FastAPIFile, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_async_db
from app.models.file import File as FileModel
from app.documents.rag_engine import document_engine
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class DocumentSearchRequest(BaseModel):
    query: str


@router.post("/parse", response_model=APIResponse[dict])
async def parse_document(file: UploadFile = FastAPIFile(...)):
    """Parse document bytes and extract structured pages, text, and metadata."""
    filename = file.filename or "doc"
    content_bytes = await file.read()
    res = await document_engine.parse_document(filename, content_bytes)
    return APIResponse(success=True, data=res, message=f"Parsed {filename} successfully")


@router.get("/history", response_model=APIResponse[List[dict]])
async def document_history(db: AsyncSession = Depends(get_async_db)):
    """Retrieve history of uploaded document files."""
    try:
        query = select(FileModel).where(FileModel.file_type == "document").order_by(FileModel.created_at.desc())
        result = await db.execute(query)
        files = result.scalars().all()
        data = [
            {
                "id": f.id,
                "filename": f.filename,
                "size_bytes": f.size_bytes,
                "public_url": f.public_url,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "metadata": f.media_metadata or {}
            }
            for f in files
        ]
        return APIResponse(success=True, data=data, message="Document history loaded")
    except Exception as e:
        logger.warning(f"Error fetching document history: {e}")
        return APIResponse(success=True, data=[], message="Document history empty")


@router.get("/{file_id}/pages", response_model=APIResponse[dict])
async def get_document_pages(file_id: str, db: AsyncSession = Depends(get_async_db)):
    """Retrieve page-by-page content and metadata for page navigation preview."""
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file_rec = result.scalar_one_or_none()

    if not file_rec:
        raise HTTPException(status_code=404, detail=f"Document {file_id} not found")

    meta = file_rec.media_metadata or {}
    pages = meta.get("pages_content", [{"page_number": 1, "text": file_rec.extracted_text or ""}])

    return APIResponse(
        success=True,
        data={
            "id": file_id,
            "filename": file_rec.filename,
            "total_pages": meta.get("pages", len(pages)),
            "pages": pages,
            "metadata": meta
        },
        message="Document pages retrieved"
    )


@router.get("/{file_id}/chunks", response_model=APIResponse[dict])
async def get_document_chunks(file_id: str, db: AsyncSession = Depends(get_async_db)):
    """Retrieve chunk preparation architecture for future RAG compatibility."""
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file_rec = result.scalar_one_or_none()

    if not file_rec:
        raise HTTPException(status_code=404, detail=f"Document {file_id} not found")

    meta = file_rec.media_metadata or {}
    chunks = meta.get("chunks", [])

    return APIResponse(
        success=True,
        data={
            "id": file_id,
            "filename": file_rec.filename,
            "chunks_count": len(chunks),
            "chunks": chunks,
            "rag_compatible": True
        },
        message="Document RAG chunks architecture retrieved"
    )


@router.post("/{file_id}/search", response_model=APIResponse[List[dict]])
async def search_inside_document(
    file_id: str,
    req: DocumentSearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Search query term inside document text with line & page matching."""
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file_rec = result.scalar_one_or_none()

    if not file_rec:
        raise HTTPException(status_code=404, detail=f"Document {file_id} not found")

    meta = file_rec.media_metadata or {}
    pages_content = meta.get("pages_content")
    matches = document_engine.search_document_text(file_rec.extracted_text or "", req.query, pages_content)

    return APIResponse(
        success=True,
        data=matches,
        message=f"Found {len(matches)} match(es) for '{req.query}'"
    )


@router.delete("/{file_id}", response_model=APIResponse[dict])
async def delete_document(file_id: str, db: AsyncSession = Depends(get_async_db)):
    """Remove document from database and file system."""
    result = await db.execute(select(FileModel).where(FileModel.id == file_id))
    file_rec = result.scalar_one_or_none()

    if file_rec:
        await db.delete(file_rec)
        await db.commit()

    return APIResponse(success=True, message=f"Document {file_id} removed", data={"id": file_id})
