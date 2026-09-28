from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, JSON, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base

class Folder(Base):
    __tablename__ = "folders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    color = Column(String(30), default="#06b6d4")
    icon = Column(String(30), default="📁")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="folders")
    files = relationship("File", back_populates="folder")

class File(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chat_id = Column(String(36), ForeignKey("chats.id", ondelete="SET NULL"), nullable=True, index=True)
    folder_id = Column(String(36), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # 'document', 'image', 'audio', 'video'
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String(1024), nullable=False) # Supabase Storage Key / Local Path
    public_url = Column(String(1024), nullable=True)
    extracted_text = Column(Text, nullable=True) # OCR or parsed text content
    vector_point_id = Column(String(255), nullable=True) # Qdrant Point ID
    media_metadata = Column(JSON, default=dict) # pages, resolution, duration, audio_channels
    is_starred = Column(Boolean, default=False)
    is_bookmarked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False) # Recycle Bin
    deleted_at = Column(DateTime, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="files")
    folder = relationship("Folder", back_populates="files")

class ImageGenerationRecord(Base):
    __tablename__ = "image_generation_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    aspect_ratio = Column(String(20), default="1:1") # '1:1', '16:9', '9:16'
    quality = Column(String(20), default="standard")
    image_url = Column(String(1024), nullable=False)
    model_used = Column(String(100), default="gemini-2.5-flash")
    generation_metadata = Column(JSON, default=dict)
    is_starred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
