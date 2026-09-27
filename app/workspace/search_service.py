"""
AetherMind Multimodal AI — Global Workspace Search Service (Phase 9)
Searches across Chats, Files, Images, Documents, Audio, Projects, Long-Term Memory, and Knowledge Base.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.workspace import Project
from app.models.file import File as FileModel, ImageGenerationRecord
from app.models.chat import Chat
from app.models.memory import MemoryMetadata, KnowledgeDocument
from app.logging.logger import logger


class GlobalWorkspaceSearchService:
    """Global Workspace Search Engine across all entities"""

    async def global_search(
        self,
        db: AsyncSession,
        user_id: str,
        query: str,
        entity_filter: Optional[str] = None # 'chats', 'files', 'projects', 'memories', 'all'
    ) -> Dict[str, Any]:
        """Perform unified global workspace search."""
        if not query:
            return {"query": query, "results": [], "total_matches": 0}

        results = []
        search_pattern = f"%{query}%"

        try:
            # 1. Search Chats
            if entity_filter in ["chats", "all", None]:
                c_res = await db.execute(
                    select(Chat)
                    .where(Chat.user_id == user_id, Chat.title.ilike(search_pattern))
                    .limit(5)
                )
                chats = c_res.scalars().all()
                for c in chats:
                    results.append({
                        "entity_type": "chat",
                        "id": c.id,
                        "title": c.title,
                        "subtitle": f"Model: {c.selected_model}",
                        "url": f"/chat/{c.id}"
                    })

            # 2. Search Files (Documents, Images, Audio)
            if entity_filter in ["files", "documents", "images", "audio", "all", None]:
                f_res = await db.execute(
                    select(FileModel)
                    .where(
                        FileModel.user_id == user_id,
                        FileModel.is_deleted == False,
                        or_(FileModel.filename.ilike(search_pattern), FileModel.extracted_text.ilike(search_pattern))
                    )
                    .limit(8)
                )
                files = f_res.scalars().all()
                for f in files:
                    results.append({
                        "entity_type": f.file_type, # 'document', 'image', 'audio'
                        "id": f.id,
                        "title": f.filename,
                        "subtitle": f"{f.file_type.upper()} • {f.mime_type}",
                        "public_url": f.public_url
                    })

            # 3. Search Projects
            if entity_filter in ["projects", "all", None]:
                p_res = await db.execute(
                    select(Project)
                    .where(Project.user_id == user_id, Project.name.ilike(search_pattern))
                    .limit(5)
                )
                projs = p_res.scalars().all()
                for p in projs:
                    results.append({
                        "entity_type": "project",
                        "id": p.id,
                        "title": f"{p.icon} {p.name}",
                        "subtitle": p.description or "Project Container"
                    })

            # 4. Search Long-Term Memory
            if entity_filter in ["memories", "all", None]:
                m_res = await db.execute(
                    select(MemoryMetadata)
                    .where(
                        MemoryMetadata.user_id == user_id,
                        or_(MemoryMetadata.memory_key.ilike(search_pattern), MemoryMetadata.memory_value.ilike(search_pattern))
                    )
                    .limit(5)
                )
                mems = m_res.scalars().all()
                for m in mems:
                    results.append({
                        "entity_type": "memory",
                        "id": m.id,
                        "title": f"Memory: {m.memory_key}",
                        "subtitle": m.memory_value
                    })

            return {
                "query": query,
                "total_matches": len(results),
                "results": results
            }

        except Exception as e:
            logger.warning(f"Error executing global search: {e}")
            return {"query": query, "total_matches": 0, "results": []}


global_search_service = GlobalWorkspaceSearchService()
