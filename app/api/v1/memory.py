"""
AetherMind Multimodal AI — Memory Engine API (Phase 8)
Supports 8 Memory Types (Conversation, Document, Image, Preference, Pinned, Temporary, Persistent, Session), Pinning, Summarization, and Compression.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.memory.memory_service import memory_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class AddMemoryRequest(BaseModel):
    memory_key: str
    memory_value: str
    memory_type: Optional[str] = "persistent" # conversation, document, image, preference, pinned, temporary, persistent, session
    category: Optional[str] = "general"
    importance_score: Optional[float] = 1.0
    is_pinned: Optional[bool] = False


@router.post("", response_model=APIResponse[dict])
async def add_memory(req: AddMemoryRequest, db: AsyncSession = Depends(get_async_db)):
    """Add a long-term memory point, generate vector embedding, and index in Qdrant."""
    res = await memory_service.add_memory(
        db=db,
        user_id="default-user-id",
        memory_key=req.memory_key,
        memory_value=req.memory_value,
        memory_type=req.memory_type or "persistent",
        category=req.category or "general",
        importance_score=req.importance_score or 1.0,
        is_pinned=req.is_pinned or False
    )
    return APIResponse(success=True, data=res, message="Memory item stored and indexed")


@router.get("", response_model=APIResponse[List[dict]])
async def list_memories(
    memory_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve long-term memory items for user."""
    memories = await memory_service.list_memories(db=db, user_id="default-user-id", memory_type=memory_type)
    return APIResponse(success=True, data=memories, message="Memories list loaded")


@router.post("/compress/{chat_id}", response_model=APIResponse[dict])
async def compress_conversation_memory(chat_id: str, db: AsyncSession = Depends(get_async_db)):
    """Compress active conversation trajectory into long-term Memory points."""
    res = await memory_service.compress_conversation(db=db, chat_id=chat_id, user_id="default-user-id")
    return APIResponse(success=True, data=res, message="Conversation trajectory compressed into long-term memory")


@router.delete("/{memory_id}", response_model=APIResponse[dict])
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete long-term memory point."""
    success = await memory_service.delete_memory(db=db, memory_id=memory_id)
    return APIResponse(success=success, message=f"Memory {memory_id} deleted", data={"id": memory_id})
