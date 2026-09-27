"""
AetherMind Multimodal AI — Cloud Workspace Core Service (Phase 9)
Manages Workspace Metadata, Activity Timeline Logging, Recycle Bin (Delete, Restore, Empty Bin), Bookmarks & Favorites.
"""

import uuid
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func

from app.models.workspace import Project, Bookmark, ActivityLog, WorkspaceMetadata
from app.models.file import File as FileModel, Folder
from app.models.chat import Chat
from app.logging.logger import logger


class WorkspaceService:
    """Cloud Workspace Core Manager"""

    async def log_activity(
        self,
        db: AsyncSession,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        details: Optional[str] = None
    ):
        """Log workspace audit trail activity."""
        try:
            log = ActivityLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details
            )
            db.add(log)
            await db.commit()
        except Exception as e:
            logger.warning(f"Error recording activity log: {e}")
            await db.rollback()

    async def get_activity_timeline(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve recent workspace activity timeline logs."""
        try:
            q = select(ActivityLog).where(ActivityLog.user_id == user_id).order_by(ActivityLog.created_at.desc()).limit(limit)
            res = await db.execute(q)
            logs = res.scalars().all()
            return [
                {
                    "id": l.id,
                    "action": l.action,
                    "entity_type": l.entity_type,
                    "entity_id": l.entity_id,
                    "details": l.details,
                    "created_at": l.created_at.isoformat() if l.created_at else None
                }
                for l in logs
            ]
        except Exception as e:
            logger.warning(f"Error fetching activity timeline: {e}")
            return []

    async def get_recycle_bin(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id"
    ) -> List[Dict[str, Any]]:
        """List soft-deleted items in Recycle Bin."""
        try:
            q = select(FileModel).where(FileModel.user_id == user_id, FileModel.is_deleted == True).order_by(FileModel.deleted_at.desc())
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
                    "deleted_at": f.deleted_at.isoformat() if f.deleted_at else None
                }
                for f in files
            ]
        except Exception as e:
            logger.warning(f"Error fetching recycle bin: {e}")
            return []

    async def restore_from_recycle_bin(self, db: AsyncSession, file_id: str, user_id: str = "default-user-id") -> bool:
        """Restore file from Recycle Bin."""
        try:
            q = select(FileModel).where(FileModel.id == file_id, FileModel.user_id == user_id)
            res = await db.execute(q)
            f = res.scalar_one_or_none()
            if f:
                f.is_deleted = False
                f.deleted_at = None
                await db.commit()
                await self.log_activity(db, user_id, "restore_file", "file", file_id, f"Restored file '{f.filename}'")
                return True
            return False
        except Exception:
            await db.rollback()
            return False

    async def empty_recycle_bin(self, db: AsyncSession, user_id: str = "default-user-id") -> int:
        """Permanently delete all items in Recycle Bin."""
        try:
            q = select(FileModel).where(FileModel.user_id == user_id, FileModel.is_deleted == True)
            res = await db.execute(q)
            files = res.scalars().all()
            count = len(files)
            for f in files:
                if f.storage_path and os.path.exists(f.storage_path):
                    try:
                        os.remove(f.storage_path)
                    except Exception:
                        pass
                await db.delete(f)
            await db.commit()
            await self.log_activity(db, user_id, "empty_recycle_bin", "workspace", None, f"Permanently deleted {count} items")
            return count
        except Exception as e:
            logger.warning(f"Error emptying recycle bin: {e}")
            await db.rollback()
            return 0


workspace_service = WorkspaceService()
