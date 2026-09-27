from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base

class MemoryMetadata(Base):
    __tablename__ = "memory_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_key = Column(String(255), nullable=False)
    memory_value = Column(Text, nullable=False)
    category = Column(String(100), default="general")
    confidence_score = Column(Float, default=1.0)
    qdrant_vector_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="memories")
