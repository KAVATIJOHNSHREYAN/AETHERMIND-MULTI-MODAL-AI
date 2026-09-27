"""
AetherMind Multimodal AI — Cloud Workspace & Productivity System Models (Phase 8/9)
Defines Project, Bookmark, ActivityLog, WorkspaceMetadata database models.
"""

from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, JSON, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base


class Project(Base):
    """Productivity Project Workspace Container"""
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(30), default="#06b6d4")
    icon = Column(String(30), default="🚀")
    is_archived = Column(Boolean, default=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="projects")


class Bookmark(Base):
    """User Bookmarks & Favorite Quick Access Links"""
    __tablename__ = "bookmarks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False) # file, chat, project, document, image, audio
    item_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ActivityLog(Base):
    """Audit Trail & Workspace Activity Timeline"""
    __tablename__ = "activity_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False) # create_project, upload_file, move_file, delete_file, restore_file, generate_image
    entity_type = Column(String(50), nullable=False) # project, folder, file, chat, memory
    entity_id = Column(String(36), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WorkspaceMetadata(Base):
    """Storage Quota & Workspace Usage Statistics"""
    __tablename__ = "workspace_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    storage_quota_bytes = Column(BigInteger, default=53687091200) # 50 GB Default Quota
    used_storage_bytes = Column(BigInteger, default=0)
    total_files = Column(Integer, default=0)
    total_projects = Column(Integer, default=0)
    total_chats = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
