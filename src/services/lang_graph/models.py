from sqlalchemy import String, Text, func, TIMESTAMP, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import datetime
from src.db.database import Base


class ShortTermMemory(Base):
    __tablename__ = 'langgraph_memory_short_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' ou 'eai'
    content_raw: Mapped[dict] = mapped_column(JSON, nullable=True) # JSON da resposta do EAI
    type: Mapped[str] = mapped_column(String(50), default='history', nullable=False) # 'history'
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

class LongTermMemory(Base):
    __tablename__ = 'langgraph_memory_long_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' ou 'eai'
    embedding: Mapped[Vector] = mapped_column(Vector(768)) # Dimensão do textembedding-gecko
    type: Mapped[str] = mapped_column(String(50), default='embedding', nullable=False) # 'embedding'
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
