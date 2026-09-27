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
        """List user projects."""
        try:
            q = select(Project).where(Project.user_id == user_id)
            if not include_archived:
                q = q.where(Project.is_archived == False)
            q = q.order_by(Project.created_at.desc())
            res = await db.execute(q)
            projs = res.scalars().all()
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "color": p.color,
                    "icon": p.icon,
                    "is_archived": p.is_archived,
                    "tags": p.tags or [],
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in projs
            ]
        except Exception as e:
            logger.warning(f"Error listing projects: {e}")
            return []

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

    async def delete_project(self, db: AsyncSession, project_id: str) -> bool:
        """Delete project."""
        try:
            res = await db.execute(select(Project).where(Project.id == project_id))
            p = res.scalar_one_or_none()
            if p:
                await db.delete(p)
                await db.commit()
                return True
            return False
        except Exception:
            await db.rollback()
            return False


project_service = ProjectService()
