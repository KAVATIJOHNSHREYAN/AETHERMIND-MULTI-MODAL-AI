"""
AetherMind Multimodal AI — Workspace Dashboard API (Phase 9)
Provides Workspace Overview Statistics, Storage Breakdown, Usage Metrics, Recent Conversations, and Recent Uploads.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.workspace.dashboard_service import dashboard_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


from app.core.dependencies import get_current_user_or_session
from app.models.user import User

@router.get("", response_model=APIResponse[dict])
@router.get("/", response_model=APIResponse[dict])
@router.get("/stats", response_model=APIResponse[dict])
@router.get("/overview", response_model=APIResponse[dict])
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve Workspace Overview Dashboard analytics & storage statistics."""
    data = await dashboard_service.get_dashboard_overview(db=db, user_id=current_user.id)
    return APIResponse(success=True, data=data, message="Workspace Dashboard overview loaded")
