from sqlalchemy import String, Text, func, TIMESTAMP, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import datetime
from typing import Optional, Dict, Any
from src.db.database import Base


class ShortTermMemory(Base):
    """Unified memory storage with embeddings for both short-term and long-term memory"""
    __tablename__ = 'langgraph_memory_short_term'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'user' or 'assistant'
    content_raw: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default='history', nullable=False)  # 'history' or 'embedding'
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(768), nullable=True)  # Google embedding dimension
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_embedding_hnsw', 'embedding', postgresql_using='hnsw'),
    )


class MemoryRetrievalLog(Base):
    """Log table for memory retrieval operations"""
    __tablename__ = 'memory_retrieval_logs'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_memories: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_user_session_log', 'user_id', 'session_id'),
        Index('idx_created_at_log', 'created_at'),
    ) 