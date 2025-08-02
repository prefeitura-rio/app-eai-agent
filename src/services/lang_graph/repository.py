from sqlalchemy.orm import Session
from sqlalchemy import select, desc, union_all, literal_column, text
from src.services.lang_graph.models import ShortTermMemory, LongTermMemory
from typing import Optional, List, Dict, Any

class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_message(
        self, user_id: str, content: str, content_type: str, embedding: list[float], content_raw: Optional[Dict[str, Any]] = None
    ):
        short_term = ShortTermMemory(
            user_id=user_id, content=content, content_type=content_type, content_raw=content_raw
        )
        long_term = LongTermMemory(
            user_id=user_id,
            content=content,
            content_type=content_type,
            embedding=embedding,
        )
        self.session.add_all([short_term, long_term])
        self.session.commit()

    def get_unified_memory(
        self, user_id: str, query_embedding: list[float], history_limit: int = 10, embedding_limit: int = 5
    ) -> List[Dict[str, Any]]:
        
        # Query para memória de longo prazo (embeddings)
        embedding_query = (
            select(
                LongTermMemory.content,
                LongTermMemory.content_type,
                literal_column("'embedding'").label("type"),
                LongTermMemory.created_at
            )
            .where(LongTermMemory.user_id == user_id)
            .order_by(LongTermMemory.embedding.cosine_distance(query_embedding))
            .limit(embedding_limit)
        )

        # Query para memória de curto prazo (histórico)
        history_query = (
            select(
                ShortTermMemory.content,
                ShortTermMemory.content_type,
                literal_column("'history'").label("type"),
                ShortTermMemory.created_at
            )
            .where(ShortTermMemory.user_id == user_id)
            .order_by(desc(ShortTermMemory.created_at))
            .limit(history_limit)
        )
        
        # Unifica as duas queries
        unified_query = union_all(embedding_query, history_query)
        
        result = self.session.execute(unified_query)
        
        # Retorna os resultados como uma lista de dicionários para facilitar o processamento
        return [row._asdict() for row in result.all()]
