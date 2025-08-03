from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class MemoryType(str, Enum):
    """Tipos de memória disponíveis para o agente."""

    USER_PROFILE = "user_profile"
    PREFERENCE = "preference"
    GOAL = "goal"
    CONSTRAINT = "constraint"
    CRITICAL_INFO = "critical_info"


class MemoryTypeConfig(BaseModel):
    """Configuração dos tipos de memória com descrições que serão injetadas no prompt do agente."""

    user_profile: str = (
        "Fatos estáveis sobre o usuário (Ex: 'O nome do usuário é Carlos', 'O usuário mora em São Paulo')."
    )
    preference: str = (
        "Preferências subjetivas e gostos do usuário (Ex: 'Prefere hotéis com academia', 'Gosta de comida italiana')."
    )
    goal: str = (
        "Um objetivo ou tarefa que o usuário deseja alcançar (Ex: 'Está planejando uma viagem de 10 dias para a Itália em dezembro')."
    )
    constraint: str = (
        "Uma restrição ou condição que deve ser respeitada (Ex: 'É alérgico a amendoim', 'Tem um orçamento máximo de R$ 5.000 para a viagem')."
    )
    critical_info: str = (
        "Informação crítica e pontual, geralmente de curto prazo (Ex: 'O número da reserva do voo é ABC123', 'O protocolo do último atendimento foi 987654')."
    )


class MemoryResponse(BaseModel):
    """Modelo para resposta de memória."""

    memory_id: str
    content: str
    memory_type: MemoryType
    creation_datetime: datetime
    last_accessed: datetime
    relevance_score: Optional[float] = None


class MemoryCreateRequest(BaseModel):
    """Modelo para criação de memória."""

    content: str = Field(..., min_length=1, max_length=1000)
    memory_type: MemoryType


class MemoryUpdateRequest(BaseModel):
    """Modelo para atualização de memória."""

    memory_id: str
    new_content: str = Field(..., min_length=1, max_length=1000)


class MemoryDeleteRequest(BaseModel):
    """Modelo para exclusão de memória."""

    memory_id: str


class MemorySearchRequest(BaseModel):
    """Modelo para busca de memórias."""

    mode: str = Field(..., pattern="^(semantic|chronological)$")
    query: Optional[str] = None
    memory_type: Optional[MemoryType] = None


class SessionConfig(BaseModel):
    """Configuração da sessão do chatbot."""

    thread_id: str
    user_id: str
    chat_model: str = "gemini-2.5-flash-lite"
    system_prompt: str = "Você é um assistente útil e amigável com memória de longo prazo."
    memory_limit: int = 20
    memory_min_relevance: float = 0.6
    enable_proactive_memory_retrieval: bool = True
    memory_types_config: MemoryTypeConfig = Field(default_factory=MemoryTypeConfig)


class SessionState(BaseModel):
    """Estado da sessão."""

    config: SessionConfig
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class ToolOutput(BaseModel):
    """Saída de uma ferramenta."""

    tool_name: str
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None


class GraphState(BaseModel):
    """Estado do grafo LangGraph."""

    messages: List[Dict[str, Any]] = Field(default_factory=list)
    retrieved_memories: List[MemoryResponse] = Field(default_factory=list)
    tool_outputs: List[ToolOutput] = Field(default_factory=list)
    config: SessionConfig
    current_step: str = "start"


class MemoryOperationResult(BaseModel):
    """Resultado de operação de memória."""

    success: bool
    memory_id: Optional[str] = None
    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    error_message: Optional[str] = None
    memories: Optional[List[MemoryResponse]] = None


class ChatMessage(BaseModel):
    """Mensagem do chat."""

    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatResponse(BaseModel):
    """Resposta do chat."""

    message: str
    memories_used: List[MemoryResponse] = Field(default_factory=list)
    tools_called: List[str] = Field(default_factory=list)
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
