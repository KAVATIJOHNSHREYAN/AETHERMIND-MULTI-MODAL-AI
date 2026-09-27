"""
AetherMind Multimodal AI — Memory, RAG & Knowledge Base Database Models (Phase 8)
Defines MemoryMetadata, KnowledgeCollection, KnowledgeDocument, EmbeddingReference, RetrievalHistory, SearchHistory, ContextHistory.
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.base import Base


class MemoryMetadata(Base):
    """Long-Term & Multi-Type Memory Store"""
    __tablename__ = "memory_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type = Column(String(50), default="persistent", index=True) # conversation, document, image, preference, pinned, temporary, persistent, session
    memory_key = Column(String(255), nullable=False)
    memory_value = Column(Text, nullable=False)
    category = Column(String(100), default="general", index=True)
    importance_score = Column(Float, default=1.0)
    is_pinned = Column(Boolean, default=False)
    qdrant_vector_id = Column(String(255), nullable=True)
    extra_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="memories")


class KnowledgeCollection(Base):
    """Knowledge Base Collection Container"""
    __tablename__ = "knowledge_collections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    qdrant_collection_name = Column(String(255), nullable=False)
    doc_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    documents = relationship("KnowledgeDocument", back_populates="collection", cascade="all, delete-orphan")


class KnowledgeDocument(Base):
    """Document Ingested inside a Knowledge Collection"""
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String(36), ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(String(36), ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # pdf, docx, md, txt
    content = Column(Text, nullable=False)
    chunk_count = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    doc_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    collection = relationship("KnowledgeCollection", back_populates="documents")


class EmbeddingReference(Base):
    """Tracks Embedding Generation & Provider Metadata"""
    __tablename__ = "embedding_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False) # document_chunk, memory, message
    entity_id = Column(String(36), nullable=False, index=True)
    provider_name = Column(String(100), default="openai") # openai, gemini, cohere, local_synthetic
    model_name = Column(String(100), default="text-embedding-3-small")
    dimensions = Column(Integer, default=1536)
    qdrant_point_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RetrievalHistory(Base):
    """Tracks RAG Retrieval Trajectory & Accuracy Metrics"""
    __tablename__ = "retrieval_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    retrieved_chunks_count = Column(Integer, default=0)
    top_similarity_score = Column(Float, default=0.0)
    retrieval_type = Column(String(50), default="hybrid") # hybrid, semantic, keyword
    retrieved_payload = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SearchHistory(Base):
    """Tracks User Semantic & Keyword Searches"""
    __tablename__ = "search_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    search_type = Column(String(50), default="semantic")
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ContextHistory(Base):
    """Tracks Conversation Context Compression & Summaries"""
    __tablename__ = "context_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    context_summary = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
