"""
AetherMind Multimodal AI — Projects API (Phase 9)
Supports Project CRUD, Archiving, Moving Conversations/Files into Projects.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.workspace.project_service import project_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#06b6d4"
    icon: Optional[str] = "🚀"
    tags: List[str] = []


class MoveToProjectRequest(BaseModel):
    item_type: str # 'chat' or 'file'
    item_id: str
    project_id: Optional[str] = None


from app.core.dependencies import get_current_user_or_session
from app.models.user import User

@router.post("", response_model=APIResponse[dict])
async def create_project(
    req: CreateProjectRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new Project Workspace container."""
    res = await project_service.create_project(
        db=db,
        user_id=current_user.id,
        name=req.name,
        description=req.description,
        color=req.color or "#06b6d4",
        icon=req.icon or "🚀",
        tags=req.tags
    )
    return APIResponse(success=True, data=res, message=f"Project '{req.name}' created")


@router.get("", response_model=APIResponse[List[dict]])
async def list_projects(
    include_archived: bool = False,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """List all projects for user."""
    projs = await project_service.list_projects(db=db, user_id=current_user.id, include_archived=include_archived)
    return APIResponse(success=True, data=projs, message="Projects list loaded")


@router.post("/move-item", response_model=APIResponse[dict])
async def move_item_to_project(
    req: MoveToProjectRequest,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Move conversation or file into a Project container."""
    success = await project_service.move_item_to_project(
        db=db, item_type=req.item_type, item_id=req.item_id, project_id=req.project_id
    )
    return APIResponse(success=success, message=f"Moved {req.item_type} to project", data={"item_id": req.item_id})


@router.post("/{project_id}/archive", response_model=APIResponse[dict])
async def archive_project(
    project_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Toggle project archive status."""
    success = await project_service.archive_project(db=db, project_id=project_id)
    return APIResponse(success=success, message="Project archive status updated", data={"id": project_id})


@router.delete("/{project_id}", response_model=APIResponse[dict])
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user_or_session),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a project container."""
    success = await project_service.delete_project(db=db, project_id=project_id)
    return APIResponse(success=success, message=f"Project {project_id} deleted", data={"id": project_id})
