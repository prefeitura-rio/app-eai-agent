from typing import Optional
import logging
from sqlalchemy import create_engine, Column, String, Text, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from src.config import env

logger = logging.getLogger(__name__)

Base = declarative_base()


class LongTermMemory(Base):
    """Modelo SQLAlchemy para a tabela long_term_memory."""

    __tablename__ = "long_term_memory"

    memory_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), nullable=False, index=True)
    creation_datetime = Column(DateTime, nullable=False, server_default=func.now())
    last_accessed = Column(DateTime, nullable=False, server_default=func.now())
    embedding = Column(Vector(768), nullable=True)  # Usando Vector do pgvector


class DatabaseManager:
    """Gerenciador de conexão com o banco de dados."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def initialize_engine(self):
        """Inicializa o engine SQLAlchemy."""
        try:
            # Usar PG_URI diretamente
            self.engine = create_engine(env.PG_URI, pool_pre_ping=True)

            # Criar session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            logger.info("Engine SQLAlchemy inicializado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao inicializar engine SQLAlchemy: {e}")
            raise

    def create_tables(self):
        """Cria as tabelas no banco de dados."""
        try:
            # Criar tabelas
            Base.metadata.create_all(bind=self.engine)

            # Criar extensão pgvector se não existir
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            logger.info("Tabelas criadas com sucesso via SQLAlchemy")

        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise

    def get_session(self):
        """Retorna uma sessão do banco de dados."""
        if not self.SessionLocal:
            raise RuntimeError(
                "DatabaseManager não foi inicializado. Chame initialize_engine() primeiro."
            )
        return self.SessionLocal()

    def close(self):
        """Fecha o engine SQLAlchemy."""
        if self.engine:
            self.engine.dispose()
            logger.info("Engine SQLAlchemy fechado")


# Instância global
db_manager = DatabaseManager()
