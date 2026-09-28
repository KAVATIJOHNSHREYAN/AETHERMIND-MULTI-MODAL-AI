from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(20), default="dark", nullable=False)
    default_model = Column(String(100), default="gemini-2.0-flash", nullable=False)
    enable_memory = Column(Boolean, default=True)
    enable_search = Column(Boolean, default=True)
    voice_accent = Column(String(50), default="en-US-Neural2-F")
    custom_instructions = Column(String(2000), nullable=True)
    preferences_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="settings")

class ProviderSettings(Base):
    __tablename__ = "provider_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name = Column(String(100), nullable=False)
    api_key_encrypted = Column(String(1024), nullable=True)
    is_enabled = Column(Boolean, default=True)
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="provider_settings")
