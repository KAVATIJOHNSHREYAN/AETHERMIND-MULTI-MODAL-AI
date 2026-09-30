"""
AetherMind Multimodal AI — Cloud Workspace Core API (Phase 9)
Supports Global Workspace Search, Activity Timeline Logs, Recycle Bin (Restore, Empty Bin), Media Gallery, and Document/Audio Libraries.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.workspace.workspace_service import workspace_service
from app.workspace.media_service import media_service
from app.workspace.search_service import global_search_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class GlobalSearchRequest(BaseModel):
    query: str
    entity_filter: Optional[str] = "all"


from app.core.dependencies import get_current_user_or_session
from app.models.user import User

@router.post("/search", response_model=APIResponse[dict])
async def global_workspace_search(
    req: GlobalSearchRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Global Workspace Search across Chats, Files, Images, Documents, Audio, Projects, Memory, and Knowledge Base."""
    res = await global_search_service.global_search(
        db=db, user_id=current_user.id, query=req.query, entity_filter=req.entity_filter or "all"
    )
    return APIResponse(success=True, data=res, message=f"Global search executed ({res.get('total_matches')} matches found)")


from app.workspace.dashboard_service import dashboard_service

@router.get("/dashboard", response_model=APIResponse[dict])
@router.get("/dashboard/overview", response_model=APIResponse[dict])
async def get_workspace_dashboard_overview(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Workspace Dashboard Endpoint Alias under /api/v1/workspace/dashboard."""
    data = await dashboard_service.get_dashboard_overview(db=db, user_id=current_user.id)
    return APIResponse(success=True, data=data, message="Workspace Dashboard overview loaded")

@router.get("/timeline", response_model=APIResponse[List[dict]])
async def get_activity_timeline(
    limit: int = 20,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve workspace activity timeline logs."""
    logs = await workspace_service.get_activity_timeline(db=db, user_id=current_user.id, limit=limit)
    return APIResponse(success=True, data=logs, message="Activity timeline loaded")


@router.get("/recycle-bin", response_model=APIResponse[List[dict]])
async def get_recycle_bin(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve items soft-deleted in Recycle Bin."""
    items = await workspace_service.get_recycle_bin(db=db, user_id=current_user.id)
    return APIResponse(success=True, data=items, message="Recycle bin items loaded")


@router.post("/recycle-bin/{file_id}/restore", response_model=APIResponse[dict])
async def restore_from_recycle_bin(
    file_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Restore file from Recycle Bin."""
    success = await workspace_service.restore_from_recycle_bin(db=db, file_id=file_id, user_id=current_user.id)
    return APIResponse(success=success, message="Item restored from Recycle Bin", data={"id": file_id})


@router.delete("/recycle-bin/empty", response_model=APIResponse[dict])
async def empty_recycle_bin(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Permanently delete all items in Recycle Bin."""
    count = await workspace_service.empty_recycle_bin(db=db, user_id=current_user.id)
    return APIResponse(success=True, message=f"Permanently deleted {count} items from Recycle Bin", data={"count": count})


@router.get("/media/gallery", response_model=APIResponse[List[dict]])
async def get_media_gallery(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve Image Gallery (Uploads & AI Generated Images)."""
    gallery = await media_service.get_image_gallery(db=db, user_id=current_user.id, category=category)
    return APIResponse(success=True, data=gallery, message="Media gallery loaded")


@router.get("/media/documents", response_model=APIResponse[List[dict]])
async def get_document_library(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve Document Library items."""
    docs = await media_service.get_document_library(db=db, user_id=current_user.id)
    return APIResponse(success=True, data=docs, message="Document library loaded")


@router.get("/media/audio", response_model=APIResponse[List[dict]])
async def get_audio_library(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve Audio Library (Voice Recordings, Transcripts)."""
    audio_items = await media_service.get_audio_library(db=db, user_id=current_user.id)
    return APIResponse(success=True, data=audio_items, message="Audio library loaded")
