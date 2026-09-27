"""
AetherMind Multimodal AI — Media & Document Libraries Service (Phase 9)
Manages Image Gallery, Generated Images, Audio Recordings, Voice Notes, Document Library, and Media Search.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.file import File as FileModel, ImageGenerationRecord
from app.logging.logger import logger


class MediaService:
    """Media Gallery & Document / Audio Libraries Manager"""

    async def get_image_gallery(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id",
        category: Optional[str] = None # 'generated', 'uploads', 'all'
    ) -> List[Dict[str, Any]]:
        """Retrieve images for Media Gallery (Uploads & AI Generated Images)."""
        images = []

        try:
            # 1. Fetch AI Generated Images
            if category in ["generated", "all", None]:
                g_res = await db.execute(
                    select(ImageGenerationRecord)
                    .where(ImageGenerationRecord.user_id == user_id)
                    .order_by(ImageGenerationRecord.created_at.desc())
                )
                gen_records = g_res.scalars().all()
                for g in gen_records:
                    images.append({
                        "id": g.id,
                        "title": g.prompt[:35] + ("..." if len(g.prompt) > 35 else ""),
                        "prompt": g.prompt,
                        "image_url": g.image_url,
                        "source": "generated",
                        "aspect_ratio": g.aspect_ratio,
                        "quality": g.quality,
                        "model_used": g.model_used,
                        "is_starred": g.is_starred or False,
                        "created_at": g.created_at.isoformat() if g.created_at else None
                    })

            # 2. Fetch Uploaded Images
            if category in ["uploads", "all", None]:
                u_res = await db.execute(
                    select(FileModel)
                    .where(FileModel.user_id == user_id, FileModel.file_type == "image", FileModel.is_deleted == False)
                    .order_by(FileModel.created_at.desc())
                )
                uploaded_files = u_res.scalars().all()
                for u in uploaded_files:
                    images.append({
                        "id": u.id,
                        "title": u.filename,
                        "prompt": u.extracted_text or "Uploaded Image",
                        "image_url": u.public_url,
                        "source": "upload",
                        "size_bytes": u.size_bytes,
                        "is_starred": u.is_starred or False,
                        "created_at": u.created_at.isoformat() if u.created_at else None
                    })

            images.sort(key=lambda x: x.get("created_at") or "", reverse=True)
            return images

        except Exception as e:
            logger.warning(f"Error fetching image gallery: {e}")
            return []

    async def get_document_library(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id"
    ) -> List[Dict[str, Any]]:
        """Retrieve documents for Document Library."""
        try:
            res = await db.execute(
                select(FileModel)
                .where(FileModel.user_id == user_id, FileModel.file_type == "document", FileModel.is_deleted == False)
                .order_by(FileModel.created_at.desc())
            )
            files = res.scalars().all()
            return [
                {
                    "id": f.id,
                    "title": f.filename,
                    "file_type": f.file_type,
                    "mime_type": f.mime_type,
                    "size_bytes": f.size_bytes,
                    "public_url": f.public_url,
                    "snippet": f.extracted_text[:250] if f.extracted_text else "",
                    "is_starred": f.is_starred or False,
                    "metadata": f.media_metadata or {},
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in files
            ]
        except Exception as e:
            logger.warning(f"Error fetching document library: {e}")
            return []

    async def get_audio_library(
        self,
        db: AsyncSession,
        user_id: str = "default-user-id"
    ) -> List[Dict[str, Any]]:
        """Retrieve audio files & voice notes for Audio Library."""
        try:
            res = await db.execute(
                select(FileModel)
                .where(FileModel.user_id == user_id, FileModel.file_type == "audio", FileModel.is_deleted == False)
                .order_by(FileModel.created_at.desc())
            )
            files = res.scalars().all()
            return [
                {
                    "id": f.id,
                    "title": f.filename,
                    "size_bytes": f.size_bytes,
                    "public_url": f.public_url,
                    "transcript": f.extracted_text or "",
                    "duration_seconds": (f.media_metadata or {}).get("duration_seconds", 0.0),
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in files
            ]
        except Exception as e:
            logger.warning(f"Error fetching audio library: {e}")
            return []


media_service = MediaService()
