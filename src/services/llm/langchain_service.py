# src/services/llm/langchain_service.py

import uuid
from datetime import datetime, timezone
from typing import List

# --- Imports de Dependências ---
from sqlalchemy import (
    create_engine,
    desc,
    Column,
    String,
    Text,
    DateTime,
    JSON,
    Integer,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.dialects.postgresql import UUID

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_postgres import PGVector
from src.config import env


# ==============================================================================
# 1. CONFIGURAÇÃO E MODELOS DO BANCO DE DADOS (SQLAlchemy)
# ==============================================================================

DATABASE_URL = env.PG_URI
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não foi definida no .env")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ConversationHistory(Base):
    """Modelo SQLAlchemy para o Histórico de Conversas Relacional."""

    __tablename__ = "conversation_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(
        String, nullable=False, index=True
    )  # <-- Chave para isolamento de dados do usuário
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ConversationHistory(agent_id='{self.agent_id}', type='{self.message_type}')>"


def get_db():
    """Generator para a sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# 2. CONFIGURAÇÃO DOS SERVIÇOS LANGCHAIN
# ==============================================================================

# Configurações Globais dos Modelos
# Garante que o nome do modelo está no formato correto
_embedding_model_name = env.EMBEDDING_MODEL.split("/")[-1]
EMBEDDING_MODEL_NAME = f"models/{_embedding_model_name}"

CHAT_MODEL_NAME = "gemini-1.5-flash-latest"  # Usando um modelo mais recente e estável
VECTOR_COLLECTION_NAME = "agent_hybrid_memory"


def get_embedding_model():
    """Retorna uma instância do modelo de embedding do Google."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME, task_type="retrieval_query"
    )


def get_chat_model():
    """Retorna uma instância do modelo de chat Gemini."""
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL_NAME, temperature=0.7, convert_system_message_to_human=True
    )


def get_vector_store():
    """Configura e retorna o PGVector store."""
    return PGVector(
        connection=DATABASE_URL,
        embeddings=get_embedding_model(),
        collection_name=VECTOR_COLLECTION_NAME,
        use_jsonb=True,
    )


class HybridMemoryRepository:
    """Repositório para gerenciar a memória híbrida."""

    def add_message(
        self, db: Session, agent_id: str, message: BaseMessage
    ) -> ConversationHistory:
        db_message = ConversationHistory(
            agent_id=agent_id,
            message_type=message.type,
            content=message.content,
            message_metadata=message.additional_kwargs,
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_recent_messages(
        self, db: Session, agent_id: str, k: int = 10
    ) -> List[BaseMessage]:
        # Filtro por agent_id garante o isolamento do histórico
        db_messages = (
            db.query(ConversationHistory)
            .filter(ConversationHistory.agent_id == agent_id)
            .order_by(desc(ConversationHistory.created_at))
            .limit(k)
            .all()
        )

        return [
            (
                HumanMessage(content=msg.content, id=str(msg.id))
                if msg.message_type == "human"
                else AIMessage(content=msg.content, id=str(msg.id))
            )
            for msg in reversed(db_messages)
        ]

    def get_hybrid_memory(
        self,
        db: Session,
        vector_store: PGVector,
        agent_id: str,
        query: str,
        recent_k: int,
        relevant_k: int,
    ) -> (List[BaseMessage], List[Document]):  # Retorna também os docs para debug
        recent_messages = self.get_recent_messages(db, agent_id, k=recent_k)
        recent_ids = {msg.id for msg in recent_messages}

        if not relevant_k:
            return recent_messages, []

        # O filtro `{"agent_id": agent_id}` é crucial para a segurança e isolamento dos dados
        relevant_docs = vector_store.similarity_search(
            query, k=relevant_k, filter={"agent_id": agent_id}
        )

        # Combinar e desduplicar
        final_messages = list(recent_messages)
        for doc in relevant_docs:
            db_id = doc.metadata.get("db_id")
            if db_id not in recent_ids:
                if doc.metadata.get("message_type") == "human":
                    final_messages.append(
                        HumanMessage(content=doc.page_content, id=db_id)
                    )
                else:
                    final_messages.append(AIMessage(content=doc.page_content, id=db_id))

        return final_messages, relevant_docs


# ==============================================================================
# 4. CLASSE PRINCIPAL DO AGENTE
# ==============================================================================


class ConversationalAgent:
    """
    Agente de IA multiusuário que utiliza memória híbrida e prompts de sistema.
    """

    def __init__(self):
        self.db_session_gen = get_db
        self.chat_model = get_chat_model()
        self.vector_store = get_vector_store()
        self.memory_repo = HybridMemoryRepository()

    def _save_message_to_stores(self, db: Session, agent_id: str, message: BaseMessage):
        """Salva uma mensagem no histórico relacional e no vector store."""
        db_message = self.memory_repo.add_message(db, agent_id, message)

        metadata = {
            "agent_id": agent_id,
            "message_type": message.type,
            "db_id": str(db_message.id),
        }

        document_to_vectorize = Document(
            page_content=message.content, metadata=metadata
        )

        self.vector_store.add_documents(
            [document_to_vectorize], ids=[str(db_message.id)]
        )

    def run(self, agent_id: str, agent_type: str, query: str) -> str:
        """Ponto de entrada principal para interagir com o agente."""
        db = next(self.db_session_gen())
        try:
            # 1. Preparar mensagem do usuário com metadados relevantes
            user_message = HumanMessage(
                content=query,
                additional_kwargs={
                    "request_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "originating_agent_id": agent_id,
                },
            )
            self._save_message_to_stores(db, agent_id, user_message)

            # 2. Obter prompt de sistema (hardcoded por enquanto)
            active_prompt = "Você é um assistente de IA chamado Jarvis. Seja prestativo, direto e use o histórico da conversa para manter o contexto."
            system_message = SystemMessage(content=active_prompt)

            # 3. Obter memória híbrida
            conversation_history, relevant_docs = self.memory_repo.get_hybrid_memory(
                db, self.vector_store, agent_id, query, recent_k=10, relevant_k=5
            )

            # --- DEBUGGING OUTPUT ---
            print("\n" + "=" * 20 + " DEBUG CONTEXT " + "=" * 20)
            print(f"Agente ID: {agent_id}")
            print(
                f"Histórico Recente Recuperado ({len(conversation_history) - len(relevant_docs)} mensagens):"
            )
            for msg in conversation_history:
                if msg not in [
                    HumanMessage(content=doc.page_content, id=doc.metadata.get("db_id"))
                    for doc in relevant_docs
                ]:
                    print(f"  - [{msg.type.upper()}] {msg.content[:80]}...")

            print(f"\nDocumentos Relevantes Recuperados ({len(relevant_docs)} docs):")
            for doc in relevant_docs:
                print(f"  - [DOC] Score: (N/A) | Content: {doc.page_content[:80]}...")
                print(f"    Metadata: {doc.metadata}")

            print("=" * 55 + "\n")
            # --- FIM DEBUGGING ---

            # 4. Montar prompt e invocar LLM
            full_prompt = [system_message] + conversation_history + [user_message]
            print("DEBUG: Invocando LLM...")
            ai_response = self.chat_model.invoke(full_prompt)
            print("DEBUG: LLM respondeu.")

            # 5. Salvar resposta da IA
            self._save_message_to_stores(db, agent_id, ai_response)

            return ai_response.content
        finally:
            db.close()


# ==============================================================================
# 5. PONTO DE ENTRADA PARA TESTES
# ==============================================================================


def setup_database():
    """Cria as tabelas no banco de dados se elas não existirem."""
    print("Verificando e criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas.")


if __name__ == "__main__":
    # setup_database()
    agent = ConversationalAgent()

    # Simula dois usuários diferentes (dois números de WhatsApp)
    user_1_whatsapp = "+5511999991111"

    agent_type = "assistente_geral"

    print("\n--- Agente Conversacional Multi-Usuário Iniciado ---")
    print(f"Usuário 1 (WhatsApp): {user_1_whatsapp}")
    print("Teste a conversa com ambos os usuários.")
    print("-" * 30)

    # Loop de conversação
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit", "quit"]:
            break

        try:
            response = agent.run(
                agent_id=user_1_whatsapp, agent_type=agent_type, query=user_input
            )
            print(f"Jarvis: {response}")
        except Exception as e:
            print(f"ERRO: {e}")

    print("\n--- Conversa encerrada. ---")
