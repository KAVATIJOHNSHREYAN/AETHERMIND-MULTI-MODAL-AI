"""
AetherMind Multimodal AI — Storage & File Manager Service (Phase 9)
Supports Folders CRUD, File Operations (Move, Copy, Rename, Star, Tag, Soft Delete to Recycle Bin), Bulk Actions, and Bulk ZIP Download.
"""

import os
import uuid
import zipfile
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from app.models.file import File as FileModel, Folder
from app.workspace.workspace_service import workspace_service
from app.logging.logger import logger


class StorageService:
    """File Manager & Storage System Service"""

    async def create_folder(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        parent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        color: str = "#06b6d4",
        icon: str = "📁"
    ) -> Dict[str, Any]:
        """Create new folder."""
        f_id = str(uuid.uuid4())
        rec = Folder(
            id=f_id,
            user_id=user_id,
            project_id=project_id,
            name=name,
            parent_id=parent_id,
            color=color,
            icon=icon
        )
        try:
            db.add(rec)
            await db.commit()
            await db.refresh(rec)
            await workspace_service.log_activity(db, user_id, "create_folder", "folder", f_id, f"Created folder '{name}'")
        except Exception as e:
            logger.warning(f"Error creating folder: {e}")
            await db.rollback()

        return {
            "id": f_id,
            "name": name,
            "parent_id": parent_id,
            "project_id": project_id,
            "color": color,
            "icon": icon,
            "created_at": rec.created_at.isoformat() if rec.created_at else datetime.utcnow().isoformat()
        }

    async def list_folders(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id",
        parent_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List folders."""
        try:
            q = select(Folder).where(Folder.user_id == user_id, Folder.is_deleted == False)
            if parent_id:
                q = q.where(Folder.parent_id == parent_id)
            if project_id:
                q = q.where(Folder.project_id == project_id)
            q = q.order_by(Folder.name.asc())
            res = await db.execute(q)
            folders = res.scalars().all()
            return [
                {
                    "id": f.id,
                    "name": f.name,
                    "parent_id": f.parent_id,
                    "project_id": f.project_id,
                    "color": f.color,
                    "icon": f.icon,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in folders
            ]
        except Exception as e:
            logger.warning(f"Error listing folders: {e}")
            return []

    async def list_files_manager(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id",
        folder_id: Optional[str] = None,
        project_id: Optional[str] = None,
        file_type: Optional[str] = None,
        is_starred: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve active files list (excluding soft-deleted items) with filtering & search."""
        try:
            q = select(FileModel).where(FileModel.user_id == user_id, FileModel.is_deleted == False)
            if folder_id:
                q = q.where(FileModel.folder_id == folder_id)
            if project_id:
                q = q.where(FileModel.project_id == project_id)
            if file_type:
                q = q.where(FileModel.file_type == file_type)
            if is_starred:
                q = q.where(FileModel.is_starred == True)
            if search:
                q = q.where(FileModel.filename.ilike(f"%{search}%"))

            q = q.order_by(FileModel.is_starred.desc(), FileModel.created_at.desc())
            res = await db.execute(q)
            files = res.scalars().all()

            return [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "file_type": f.file_type,
                    "mime_type": f.mime_type,
                    "size_bytes": f.size_bytes,
                    "public_url": f.public_url,
                    "folder_id": f.folder_id,
                    "project_id": f.project_id,
                    "is_starred": f.is_starred or False,
                    "is_bookmarked": f.is_bookmarked or False,
                    "tags": f.tags or [],
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in files
            ]
        except Exception as e:
            logger.warning(f"Error fetching file manager files: {e}")
            return []

    async def toggle_star_file(self, db: AsyncSession, file_id: str) -> bool:
        """Star or unstar file."""
        try:
            res = await db.execute(select(FileModel).where(FileModel.id == file_id))
            f = res.scalar_one_or_none()
            if f:
                f.is_starred = not (f.is_starred or False)
                await db.commit()
                return True
            return False
        except Exception:
            await db.rollback()
            return False

    async def move_file(self, db: AsyncSession, file_id: str, folder_id: Optional[str] = None, project_id: Optional[str] = None) -> bool:
        """Move file to folder or project."""
        try:
            res = await db.execute(select(FileModel).where(FileModel.id == file_id))
            f = res.scalar_one_or_none()
            if f:
                if folder_id is not None:
                    f.folder_id = folder_id
                if project_id is not None:
                    f.project_id = project_id
                await db.commit()
                await workspace_service.log_activity(db, f.user_id, "move_file", "file", file_id, f"Moved file '{f.filename}'")
                return True
            return False
        except Exception:
            await db.rollback()
            return False

    async def soft_delete_file(self, db: AsyncSession, file_id: str) -> bool:
        """Soft delete file to Recycle Bin."""
        try:
            res = await db.execute(select(FileModel).where(FileModel.id == file_id))
            f = res.scalar_one_or_none()
            if f:
                f.is_deleted = True
                f.deleted_at = datetime.utcnow()
                await db.commit()
                await workspace_service.log_activity(db, f.user_id, "delete_file", "file", file_id, f"Moved file '{f.filename}' to Recycle Bin")
                return True
            return False
        except Exception:
            await db.rollback()
            return False

    async def bulk_delete_files(self, db: AsyncSession, file_ids: List[str]) -> int:
        """Bulk soft delete multiple files to Recycle Bin."""
        try:
            now = datetime.utcnow()
            await db.execute(
                update(FileModel)
                .where(FileModel.id.in_(file_ids))
                .values(is_deleted=True, deleted_at=now)
            )
            await db.commit()
            return len(file_ids)
        except Exception:
            await db.rollback()
            return 0

    async def create_bulk_zip(self, db: AsyncSession, file_ids: List[str]) -> bytes:
        """Generate ZIP archive bytes for bulk downloading selected files."""
        res = await db.execute(select(FileModel).where(FileModel.id.in_(file_ids)))
        files = res.scalars().all()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f in files:
                if f.storage_path and os.path.exists(f.storage_path):
                    try:
                        zip_file.write(f.storage_path, arcname=f.filename)
                    except Exception as ze:
                        logger.warning(f"Zip file add warning: {ze}")
                else:
                    # Write synthetic content if path missing
                    zip_file.writestr(f.filename, f.extracted_text or f"[Content of {f.filename}]")

        return zip_buffer.getvalue()


storage_service = StorageService()
