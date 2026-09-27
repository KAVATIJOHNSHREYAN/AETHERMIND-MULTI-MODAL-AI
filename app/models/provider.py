from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base

class AIProviderConfig(Base):
    __tablename__ = "ai_provider_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name = Column(String(100), nullable=False, index=True) # 'openai', 'google_gemini', 'anthropic_claude', 'groq', 'openrouter', 'deepseek', 'mistral', 'together', 'cohere', 'xai', 'ollama', 'lmstudio'
    api_key_encrypted = Column(String(1024), nullable=True)
    api_base_url = Column(String(512), nullable=True)
    is_enabled = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=1) # 1 = highest
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AIModelRegistry(Base):
    __tablename__ = "ai_model_registry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_name = Column(String(100), nullable=False, index=True)
    model_id = Column(String(100), nullable=False, unique=True, index=True) # e.g. 'gemini-2.5-flash', 'gpt-4o', 'claude-3-5-sonnet'
    display_name = Column(String(255), nullable=False)
    context_window = Column(Integer, default=128000)
    supports_vision = Column(Boolean, default=True)
    supports_audio = Column(Boolean, default=False)
    supports_streaming = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
