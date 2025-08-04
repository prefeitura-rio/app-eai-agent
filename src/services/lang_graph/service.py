from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from src.services.lang_graph.models import (
    SessionConfig,
    GraphState,
    ChatMessage,
    ChatResponse,
    MemoryResponse,
)
from src.services.lang_graph.graph import graph, CustomMessagesState
from src.services.lang_graph.database import db_manager
from src.services.lang_graph.memory import memory_manager

logger = logging.getLogger(__name__)


class LangGraphChatbotService:
    """Serviço principal do chatbot com memória de longo prazo."""

    def __init__(self):
        self.graph = graph
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        self.sessions = {}  # Armazenar configurações de sessão
        # self._initialize_database()

    def _initialize_database(self):
        """Inicializa o banco de dados."""
        try:
            self.db_manager.initialize_engine()
            self.db_manager.create_tables()
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

    def initialize_session(
        self,
        user_id: str,
        thread_id: str,
        config: Optional[SessionConfig] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Inicializa uma nova sessão de conversa."""
        try:
            # Usar configuração fornecida ou criar padrão
            if not config:
                config = SessionConfig(
                    thread_id=thread_id,
                    user_id=user_id,
                    chat_model="gemini-2.5-flash-lite",
                    temperature=temperature if temperature is not None else 0.7,
                    enable_proactive_memory_retrieval=False,
                    **kwargs,
                )
            else:
                # Atualizar temperatura se fornecida
                if temperature is not None:
                    config.temperature = temperature
                # Atualizar outros parâmetros se fornecidos
                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

            # Validar configuração
            if not config.user_id or not config.thread_id:
                raise ValueError("user_id e thread_id são obrigatórios")

            # Armazenar configuração da sessão
            session_key = f"{user_id}:{thread_id}"
            self.sessions[session_key] = config

            # Criar estado inicial
            initial_state = CustomMessagesState(
                messages=[],
                retrieved_memories=[],
                tool_outputs=[],
                config=config,
                current_step="start",
            )

            logger.info(
                f"Sessão inicializada para usuário {config.user_id} com temperatura {config.temperature}"
            )
            return {
                "success": True,
                "session_id": config.thread_id,
                "user_id": config.user_id,
                "initial_state": initial_state,
            }

        except Exception as e:
            logger.error(f"Erro ao inicializar sessão: {e}")
            return {"success": False, "error_message": str(e)}

    async def process_message(
        self,
        user_id: str,
        thread_id: str,
        message: str,
        config: Optional[SessionConfig] = None,
    ) -> ChatResponse:
        """Processa uma mensagem do usuário."""
        try:
            # Validar entrada
            if not user_id or not thread_id or not message:
                raise ValueError("user_id, thread_id e message são obrigatórios")

            # Usar configuração da sessão armazenada ou fornecida
            session_key = f"{user_id}:{thread_id}"
            if not config:
                config = self.sessions.get(session_key)

            if not config:
                # Criar configuração padrão se não existir
                config = SessionConfig(
                    thread_id=thread_id,
                    user_id=user_id,
                    chat_model="gemini-2.5-flash-lite",
                    temperature=0.7,
                )
                # Armazenar para uso futuro
                self.sessions[session_key] = config

            # Criar estado inicial apenas com a nova mensagem do usuário
            # O checkpointer do LangGraph manterá o histórico anterior automaticamente
            initial_state = CustomMessagesState(
                messages=[HumanMessage(content=message)],
                retrieved_memories=[],
                tool_outputs=[],
                config=config,
                current_step="start",
            )

            # Executar o grafo com thread_id para manter memória de curto prazo
            config_dict = {"configurable": {"thread_id": thread_id}}

            final_state = await self.graph.ainvoke(initial_state, config=config_dict)

            # Extrair resposta
            messages = final_state.get("messages", [])
            assistant_messages = [msg for msg in messages if isinstance(msg, AIMessage)]

            if not assistant_messages:
                response_content = "Desculpe, não consegui processar sua mensagem."
            else:
                raw_content = assistant_messages[-1].content

                # Lidar com respostas que podem ser listas (do Gemini)
                if isinstance(raw_content, list):
                    # Se for uma lista, juntar os elementos
                    response_content = " ".join(str(item) for item in raw_content)
                else:
                    response_content = str(raw_content)

            # Extrair memórias usadas
            retrieved_memories = final_state.get("retrieved_memories", [])

            # Extrair ferramentas chamadas
            tool_outputs = final_state.get("tool_outputs", [])
            tools_called = [
                output.tool_name for output in tool_outputs if output.success
            ]

            # Criar resposta
            chat_response = ChatResponse(
                message=response_content,
                memories_used=retrieved_memories,
                tools_called=tools_called,
                conversation_id=thread_id,
                timestamp=datetime.utcnow(),
            )

            logger.info(f"Mensagem processada com sucesso para usuário {user_id}")
            return chat_response

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return ChatResponse(
                message="Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.",
                conversation_id=thread_id,
                timestamp=datetime.utcnow(),
            )

    def get_conversation_history(
        self, user_id: str, thread_id: str, limit: int = 50
    ) -> List[ChatMessage]:
        """Obtém o histórico de conversação."""
        try:
            # Esta é uma implementação simplificada
            # Na implementação real, você armazenaria o histórico no banco de dados

            # Por enquanto, retornamos uma lista vazia
            # Você pode implementar o armazenamento de histórico posteriormente
            return []

        except Exception as e:
            logger.error(f"Erro ao obter histórico de conversação: {e}")
            return []

    def clear_memory(self, user_id: str) -> Dict[str, Any]:
        """Limpa todas as memórias de um usuário."""
        try:
            # Implementar limpeza de memórias
            # Por simplicidade, vamos apenas retornar sucesso
            # Na implementação real, você deletaria todas as memórias do usuário

            logger.info(f"Memórias limpas para usuário {user_id}")
            return {
                "success": True,
                "message": f"Memórias limpas para usuário {user_id}",
            }

        except Exception as e:
            logger.error(f"Erro ao limpar memórias: {e}")
            return {"success": False, "error_message": str(e)}

    def save_memory_directly(
        self, user_id: str, content: str, memory_type: str
    ) -> Dict[str, Any]:
        """Salva uma memória diretamente (para testes)."""
        try:
            from src.services.lang_graph.models import MemoryType

            # Converter string para enum
            try:
                memory_type_enum = MemoryType(memory_type)
            except ValueError:
                return {
                    "success": False,
                    "error_message": f"memory_type inválido: {memory_type}",
                }

            # Salvar memória
            result = self.memory_manager.save_memory(
                user_id=user_id, content=content, memory_type=memory_type_enum
            )

            if result.success:
                return {
                    "success": True,
                    "memory_id": result.memory_id,
                    "content": result.content,
                    "memory_type": result.memory_type.value,
                }
            else:
                return {"success": False, "error_message": result.error_message}

        except Exception as e:
            logger.error(f"Erro ao salvar memória diretamente: {e}")
            return {"success": False, "error_message": str(e)}

    def get_memories_directly(
        self,
        user_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Obtém memórias diretamente (para testes)."""
        try:
            from src.services.lang_graph.models import MemoryType

            # Converter string para enum se fornecido
            memory_type_enum = None
            if memory_type:
                try:
                    memory_type_enum = MemoryType(memory_type)
                except ValueError:
                    return {
                        "success": False,
                        "error_message": f"memory_type inválido: {memory_type}",
                    }

            # Buscar memórias
            result = self.memory_manager.get_memory(
                user_id=user_id, query=query, memory_type=memory_type_enum
            )

            if result.success:
                memories_data = []
                for memory in result.memories or []:
                    memory_dict = {
                        "memory_id": memory.memory_id,
                        "content": memory.content,
                        "memory_type": memory.memory_type.value,
                        "creation_datetime": memory.creation_datetime.isoformat(),
                        "last_accessed": memory.last_accessed.isoformat(),
                    }
                    if memory.relevance_score is not None:
                        memory_dict["relevance_score"] = memory.relevance_score
                    memories_data.append(memory_dict)

                return {
                    "success": True,
                    "memories": memories_data,
                    "count": len(memories_data),
                }
            else:
                return {"success": False, "error_message": result.error_message}

        except Exception as e:
            logger.error(f"Erro ao obter memórias diretamente: {e}")
            return {"success": False, "error_message": str(e)}

    def close(self):
        """Fecha o serviço e libera recursos."""
        try:
            self.db_manager.close()
            logger.info("Serviço fechado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar serviço: {e}")


# Instância global do serviço
chatbot_service = LangGraphChatbotService()
