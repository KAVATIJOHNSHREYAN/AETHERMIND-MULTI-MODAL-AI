"""
AetherMind Multimodal AI — Workspace Dashboard Service (Phase 9)
Provides Workspace Overview Statistics, Storage Breakdown, AI Usage Metrics, Recent Conversations, Recent Uploads, and Pinned Items.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.workspace import Project, WorkspaceMetadata
from app.models.file import File as FileModel, ImageGenerationRecord
from app.models.chat import Chat
from app.models.memory import MemoryMetadata, KnowledgeCollection
from app.logging.logger import logger


class DashboardService:
    """Workspace Dashboard & Analytics Overview Service"""

    async def get_dashboard_overview(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id"
    ) -> Dict[str, Any]:
        """Generate comprehensive Workspace Overview Dashboard metrics."""
        try:
            # 1. Total Projects Count
            p_res = await db.execute(select(func.count(Project.id)).where(Project.user_id == user_id, Project.is_archived == False))
            total_projects = p_res.scalar() or 0

            # 2. Total Conversations Count
            c_res = await db.execute(select(func.count(Chat.id)).where(Chat.user_id == user_id))
            total_chats = c_res.scalar() or 0

            # 3. Active Files Count & Storage Usage
            f_res = await db.execute(
                select(func.count(FileModel.id), func.coalesce(func.sum(FileModel.size_bytes), 0))
                .where(FileModel.user_id == user_id, FileModel.is_deleted == False)
            )
            f_row = f_res.first()
            total_files = f_row[0] if f_row else 0
            used_storage_bytes = f_row[1] if f_row else 0

            # 4. Storage Breakdown by File Type
            type_res = await db.execute(
                select(FileModel.file_type, func.count(FileModel.id), func.coalesce(func.sum(FileModel.size_bytes), 0))
                .where(FileModel.user_id == user_id, FileModel.is_deleted == False)
                .group_by(FileModel.file_type)
            )
            type_rows = type_res.all()
            storage_breakdown = {row[0]: {"count": row[1], "size_bytes": row[2]} for row in type_rows}

            # 5. AI Generations Count
            gen_res = await db.execute(select(func.count(ImageGenerationRecord.id)).where(ImageGenerationRecord.user_id == user_id))
            total_generations = gen_res.scalar() or 0

            # 6. Knowledge Base Collections Count
            kb_res = await db.execute(select(func.count(KnowledgeCollection.id)).where(KnowledgeCollection.user_id == user_id))
            total_kb_collections = kb_res.scalar() or 0

            # 7. Recent Conversations
            chat_res = await db.execute(select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).limit(5))
            recent_chats = chat_res.scalars().all()

            # 8. Recent Uploads
            up_res = await db.execute(select(FileModel).where(FileModel.user_id == user_id, FileModel.is_deleted == False).order_by(FileModel.created_at.desc()).limit(5))
            recent_uploads = up_res.scalars().all()

            # Quota: 50 GB
            quota_bytes = 53687091200
            used_mb = round(used_storage_bytes / (1024 * 1024), 2)
            used_percentage = round((used_storage_bytes / float(quota_bytes)) * 100.0, 2)

            return {
                "overview": {
                    "total_projects": total_projects,
                    "total_conversations": total_chats,
                    "total_files": total_files,
                    "total_generations": total_generations,
                    "total_kb_collections": total_kb_collections
                },
                "storage": {
                    "used_bytes": used_storage_bytes,
                    "used_mb": used_mb,
                    "quota_bytes": quota_bytes,
                    "quota_gb": 50.0,
                    "used_percentage": used_percentage,
                    "breakdown": storage_breakdown
                },
                "recent_chats": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "selected_model": c.selected_model,
                        "updated_at": c.updated_at.isoformat() if c.updated_at else None
                    }
                    for c in recent_chats
                ],
                "recent_uploads": [
                    {
                        "id": u.id,
                        "filename": u.filename,
                        "file_type": u.file_type,
                        "size_bytes": u.size_bytes,
                        "public_url": u.public_url,
                        "created_at": u.created_at.isoformat() if u.created_at else None
                    }
                    for u in recent_uploads
                ]
            }

        except Exception as e:
            logger.warning(f"Error building dashboard overview: {e}")
            return {"overview": {}, "storage": {}}


dashboard_service = DashboardService()
