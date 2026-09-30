"""
AetherMind Multimodal AI — Projects Service (Phase 9)
Supports Project CRUD, Archiving, Moving Conversations/Files/Images/Audio into Projects, and Project Dashboards.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from app.models.workspace import Project
from app.models.file import File as FileModel
from app.models.chat import Chat
from app.workspace.workspace_service import workspace_service
from app.logging.logger import logger


class ProjectService:
    """Projects Engine Manager"""

    async def create_project(
        self,
        db: AsyncSession,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        color: str = "#06b6d4",
        icon: str = "🚀",
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create new Project container."""
        proj_id = str(uuid.uuid4())
        rec = Project(
            id=proj_id,
            user_id=user_id,
            name=name,
            description=description or "",
            color=color,
            icon=icon,
            tags=tags or [],
            is_archived=False
        )
        try:
            db.add(rec)
            await db.commit()
            await db.refresh(rec)
            await workspace_service.log_activity(db, user_id, "create_project", "project", proj_id, f"Created project '{name}'")
        except Exception as e:
            logger.warning(f"Project creation warning: {e}")
            await db.rollback()

        return {
            "id": proj_id,
            "name": name,
            "description": description,
            "color": color,
            "icon": icon,
            "is_archived": False,
            "tags": tags or [],
            "created_at": rec.created_at.isoformat() if rec.created_at else datetime.utcnow().isoformat()
        }

    async def list_projects(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id",
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """List user projects with file and chat counts."""
        try:
            q = select(Project).where(Project.user_id == user_id)
            if not include_archived:
                q = q.where(Project.is_archived == False)
            q = q.order_by(Project.created_at.desc())
            res = await db.execute(q)
            projs = res.scalars().all()
            
            output = []
            for p in projs:
                file_cnt_res = await db.execute(select(FileModel).where(FileModel.project_id == p.id, FileModel.user_id == user_id, FileModel.is_deleted == False))
                file_cnt = len(file_cnt_res.scalars().all())
                
                chat_cnt_res = await db.execute(select(Chat).where(Chat.project_id == p.id, Chat.user_id == user_id))
                chat_cnt = len(chat_cnt_res.scalars().all())
                
                output.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "color": p.color,
                    "icon": p.icon,
                    "is_archived": p.is_archived,
                    "tags": p.tags or [],
                    "file_count": file_cnt,
                    "chat_count": chat_cnt,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                })
            return output
        except Exception as e:
            logger.warning(f"Error listing projects: {e}")
            return []

    async def get_project_detail(
        self,
        db: AsyncSession,
        project_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve complete project details including associated files, folders, chats, and image generations."""
        try:
            res = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id))
            p = res.scalar_one_or_none()
            if not p:
                return None
                
            files_res = await db.execute(select(FileModel).where(FileModel.project_id == project_id, FileModel.user_id == user_id, FileModel.is_deleted == False))
            files = files_res.scalars().all()
            
            folders_res = await db.execute(select(Folder).where(Folder.project_id == project_id, Folder.user_id == user_id, Folder.is_deleted == False))
            folders = folders_res.scalars().all()
            
            chats_res = await db.execute(select(Chat).where(Chat.project_id == project_id, Chat.user_id == user_id))
            chats = chats_res.scalars().all()
            
            storage_used = sum(f.size_bytes or 0 for f in files)
            
            return {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "color": p.color,
                "icon": p.icon,
                "is_archived": p.is_archived,
                "tags": p.tags or [],
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "files": [
                    {
                        "id": f.id,
                        "filename": f.filename,
                        "file_type": f.file_type,
                        "mime_type": f.mime_type,
                        "size_bytes": f.size_bytes,
                        "public_url": f.public_url,
                        "folder_id": f.folder_id,
                        "is_starred": f.is_starred or False,
                        "created_at": f.created_at.isoformat() if f.created_at else None
                    }
                    for f in files
                ],
                "folders": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "parent_id": f.parent_id,
                        "created_at": f.created_at.isoformat() if f.created_at else None
                    }
                    for f in folders
                ],
                "chats": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "created_at": c.created_at.isoformat() if c.created_at else None
                    }
                    for c in chats
                ],
                "stats": {
                    "total_files": len(files),
                    "total_folders": len(folders),
                    "total_chats": len(chats),
                    "storage_used_bytes": storage_used,
                    "storage_used_mb": round(storage_used / (1024 * 1024), 2)
                }
            }
        except Exception as e:
            logger.warning(f"Error fetching project detail: {e}")
            return None

    async def move_item_to_project(
        self,
        db: AsyncSession,
        item_type: str, # 'chat' or 'file'
        item_id: str,
        project_id: Optional[str]
    ) -> bool:
        """Move Conversation or File into a Project container."""
        try:
            if item_type == "chat":
                await db.execute(
                    update(Chat).where(Chat.id == item_id).values(project_id=project_id)
                )
            elif item_type == "file":
                await db.execute(
                    update(FileModel).where(FileModel.id == item_id).values(project_id=project_id)
                )
            await db.commit()
            return True
        except Exception as e:
            logger.warning(f"Error moving item to project: {e}")
            await db.rollback()
            return False

    async def archive_project(self, db: AsyncSession, project_id: str) -> bool:
        """Toggle project archive status."""
        try:
            res = await db.execute(select(Project).where(Project.id == project_id))
            p = res.scalar_one_or_none()
            if p:
                p.is_archived = not p.is_archived
                await db.commit()
                return True
            return False
        except Exception:
            await db.rollback()
            return False

    async def delete_project(self, db: AsyncSession, project_id: str, user_id: str = None) -> bool:
        """Cascade delete project and associated resources for the authenticated user."""
        try:
            q = select(Project).where(Project.id == project_id)
            if user_id:
                q = q.where(Project.user_id == user_id)
            res = await db.execute(q)
            p = res.scalar_one_or_none()
            if p:
                # Delete files, folders, and chats assigned to this project
                await db.execute(delete(FileModel).where(FileModel.project_id == project_id))
                await db.execute(delete(Folder).where(Folder.project_id == project_id))
                await db.execute(delete(Chat).where(Chat.project_id == project_id))
                await db.delete(p)
                await db.commit()
                if user_id:
                    await workspace_service.log_activity(db, user_id, "delete_project", "project", project_id, f"Deleted project '{p.name}'")
                return True
            return False
        except Exception as e:
            logger.warning(f"Error deleting project: {e}")
            await db.rollback()
            return False


project_service = ProjectService()
