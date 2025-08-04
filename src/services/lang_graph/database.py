from typing import Optional
import logging
from sqlalchemy import create_engine, Column, String, DateTime, Float, Text, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from src.config import env
from src.utils.log import logger


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
        self.database_url = env.PG_URI

    def initialize_engine(self):
        """Inicializa o engine SQLAlchemy."""
        try:
            self.engine = create_engine(self.database_url, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info("Engine SQLAlchemy inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar engine: {e}")
            raise

    def create_tables(self):
        """Cria as tabelas no banco de dados."""
        try:
            # Criar extensão pgvector se não existir
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()

            Base.metadata.create_all(bind=self.engine)
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
