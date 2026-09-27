"""
AetherMind Multimodal AI — File Manager & Storage Operations API (Phase 9)
Supports Folders CRUD, File Star/Favorite, Move, Soft Delete to Recycle Bin, Bulk Actions, and Bulk ZIP Download.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_db
from app.workspace.storage_service import storage_service
from app.schemas.common import APIResponse
from app.logging.logger import logger

router = APIRouter()


class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None
    project_id: Optional[str] = None
    color: Optional[str] = "#06b6d4"
    icon: Optional[str] = "📁"


class MoveFileRequest(BaseModel):
    folder_id: Optional[str] = None
    project_id: Optional[str] = None


class BulkFileRequest(BaseModel):
    file_ids: List[str]


@router.post("/folders", response_model=APIResponse[dict])
async def create_folder(req: CreateFolderRequest, db: AsyncSession = Depends(get_async_db)):
    """Create a new folder container."""
    res = await storage_service.create_folder(
        db=db,
        user_id="default-user-id",
        name=req.name,
        parent_id=req.parent_id,
        project_id=req.project_id,
        color=req.color or "#06b6d4",
        icon=req.icon or "📁"
    )
    return APIResponse(success=True, data=res, message=f"Folder '{req.name}' created")


@router.get("/folders", response_model=APIResponse[List[dict]])
async def list_folders(
    parent_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """List folders in workspace."""
    folders = await storage_service.list_folders(db=db, user_id="default-user-id", parent_id=parent_id, project_id=project_id)
    return APIResponse(success=True, data=folders, message="Folders list loaded")


@router.get("/manager", response_model=APIResponse[List[dict]])
async def list_files_manager(
    folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
    file_type: Optional[str] = None,
    is_starred: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Retrieve active workspace files for File Manager with filtering."""
    files = await storage_service.list_files_manager(
        db=db,
        user_id="default-user-id",
        folder_id=folder_id,
        project_id=project_id,
        file_type=file_type,
        is_starred=is_starred,
        search=search
    )
    return APIResponse(success=True, data=files, message="File Manager files loaded")


@router.post("/{file_id}/star", response_model=APIResponse[dict])
async def toggle_star_file(file_id: str, db: AsyncSession = Depends(get_async_db)):
    """Toggle star/favorite status on a file."""
    success = await storage_service.toggle_star_file(db=db, file_id=file_id)
    return APIResponse(success=success, message="File star status updated", data={"id": file_id})


@router.post("/{file_id}/move", response_model=APIResponse[dict])
async def move_file(file_id: str, req: MoveFileRequest, db: AsyncSession = Depends(get_async_db)):
    """Move file to specified folder or project."""
    success = await storage_service.move_file(db=db, file_id=file_id, folder_id=req.folder_id, project_id=req.project_id)
    return APIResponse(success=success, message="File moved successfully", data={"id": file_id})


@router.delete("/{file_id}/trash", response_model=APIResponse[dict])
async def soft_delete_file(file_id: str, db: AsyncSession = Depends(get_async_db)):
    """Soft delete file to Recycle Bin."""
    success = await storage_service.soft_delete_file(db=db, file_id=file_id)
    return APIResponse(success=success, message="File moved to Recycle Bin", data={"id": file_id})


@router.post("/bulk-delete", response_model=APIResponse[dict])
async def bulk_delete_files(req: BulkFileRequest, db: AsyncSession = Depends(get_async_db)):
    """Bulk soft delete files to Recycle Bin."""
    count = await storage_service.bulk_delete_files(db=db, file_ids=req.file_ids)
    return APIResponse(success=True, message=f"Moved {count} files to Recycle Bin", data={"count": count})


@router.post("/bulk-download")
async def bulk_download_files(req: BulkFileRequest, db: AsyncSession = Depends(get_async_db)):
    """Generate and stream a ZIP archive for bulk file download."""
    zip_bytes = await storage_service.create_bulk_zip(db=db, file_ids=req.file_ids)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=aethermind_workspace_files.zip"}
    )
