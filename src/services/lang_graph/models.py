from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid
from langgraph.graph import MessagesState


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

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MemoryCreateRequest(BaseModel):
    """Modelo para criação de memória."""

    content: str = Field(..., min_length=1, max_length=1000)
    memory_type: MemoryType

    @validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content não pode estar vazio")
        return v.strip()


class MemoryUpdateRequest(BaseModel):
    """Modelo para atualização de memória."""

    memory_id: str = Field(..., description="ID da memória a ser atualizada")
    new_content: str = Field(..., min_length=1, max_length=1000)

    @validator("new_content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("New content não pode estar vazio")
        return v.strip()


class MemoryDeleteRequest(BaseModel):
    """Modelo para exclusão de memória."""

    memory_id: str = Field(..., description="ID da memória a ser deletada")


class MemorySearchRequest(BaseModel):
    """Modelo para busca de memórias."""

    query: Optional[str] = Field(None, description="Query para busca semântica")
    memory_type: Optional[MemoryType] = Field(
        None, description="Tipo de memória para filtrar"
    )


# Modelos para inputs das ferramentas
class GetMemoryToolInput(BaseModel):
    """Input para a ferramenta get_memory_tool."""

    memory_type: str = Field(
        ...,
        description="Tipo de memória (user_profile, preference, goal, constraint, critical_info)",
    )
    query: str = Field(..., min_length=1, description="Query para busca semântica")

    @validator("memory_type")
    def validate_memory_type(cls, v):
        valid_types = [mt.value for mt in MemoryType]
        if v not in valid_types:
            raise ValueError(f"memory_type deve ser um dos: {valid_types}")
        return v

    @validator("query")
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query não pode estar vazio")
        return v.strip()


class SaveMemoryToolInput(BaseModel):
    """Input para a ferramenta save_memory_tool."""

    content: str = Field(
        ..., min_length=1, max_length=1000, description="Conteúdo da memória"
    )
    memory_type: str = Field(
        ...,
        description="Tipo de memória (user_profile, preference, goal, constraint, critical_info)",
    )

    @validator("memory_type")
    def validate_memory_type(cls, v):
        valid_types = [mt.value for mt in MemoryType]
        if v not in valid_types:
            raise ValueError(f"memory_type deve ser um dos: {valid_types}")
        return v

    @validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content não pode estar vazio")
        return v.strip()


class UpdateMemoryToolInput(BaseModel):
    """Input para a ferramenta update_memory_tool."""

    memory_id: str = Field(..., description="ID da memória a ser atualizada")
    new_content: str = Field(
        ..., min_length=1, max_length=1000, description="Novo conteúdo da memória"
    )

    @validator("new_content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("New content não pode estar vazio")
        return v.strip()


class DeleteMemoryToolInput(BaseModel):
    """Input para a ferramenta delete_memory_tool."""

    memory_id: str = Field(..., description="ID da memória a ser deletada")


# Modelos para outputs das ferramentas
class ToolSuccessResponse(BaseModel):
    """Resposta de sucesso de uma ferramenta."""

    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ToolErrorResponse(BaseModel):
    """Resposta de erro de uma ferramenta."""

    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class GetMemoryToolOutput(BaseModel):
    """Output da ferramenta get_memory_tool."""

    success: bool
    memories: Optional[List[MemoryResponse]] = None
    count: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


class SaveMemoryToolOutput(BaseModel):
    """Output da ferramenta save_memory_tool."""

    success: bool
    memory_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class UpdateMemoryToolOutput(BaseModel):
    """Output da ferramenta update_memory_tool."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class DeleteMemoryToolOutput(BaseModel):
    """Output da ferramenta delete_memory_tool."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class SessionConfig(BaseModel):
    """Configuração da sessão do chatbot."""

    thread_id: str = Field(..., description="ID da thread de conversa")
    user_id: str = Field(..., description="ID do usuário")
    chat_model: str = Field(
        default="gemini-2.5-flash-lite", description="Modelo de chat a ser usado"
    )
    system_prompt: str = Field(
        default="Você é um assistente útil e amigável com memória de longo prazo.",
        description="Prompt do sistema",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Controle de criatividade (0.0 = determinístico, 1.0 = muito criativo)",
    )
    memory_limit: int = Field(
        default=20, ge=1, le=100, description="Limite de memórias a buscar"
    )
    memory_min_relevance: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Relevância mínima para memórias"
    )
    enable_proactive_memory_retrieval: bool = Field(
        default=False, description="Habilitar recuperação proativa de memórias"
    )
    memory_retrieval_mode: str = Field(
        default="semantic",
        description="Modo de recuperação (semantic ou chronological)",
    )
    memory_types_config: MemoryTypeConfig = Field(default_factory=MemoryTypeConfig)


class SessionState(BaseModel):
    """Estado da sessão."""

    config: SessionConfig
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class ToolOutput(BaseModel):
    """Saída de uma ferramenta."""

    tool_name: str = Field(..., description="Nome da ferramenta")
    success: bool = Field(..., description="Se a execução foi bem-sucedida")
    data: Dict[str, Any] = Field(default_factory=dict, description="Dados da resposta")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")


class CustomMessagesState(MessagesState):
    """Estado customizado para o grafo LangGraph que herda de MessagesState."""

    retrieved_memories: List[MemoryResponse] = []
    tool_outputs: List[ToolOutput] = []
    config: SessionConfig
    current_step: str = "start"

    def __getitem__(self, key):
        """Permite acesso como dicionário."""
        if key == "config":
            return self.config
        elif key == "messages":
            return self.messages
        elif key == "retrieved_memories":
            return self.retrieved_memories
        elif key == "tool_outputs":
            return self.tool_outputs
        elif key == "current_step":
            return self.current_step
        else:
            raise KeyError(f"Chave '{key}' não encontrada")

    def __setitem__(self, key, value):
        """Permite atribuição como dicionário."""
        if key == "config":
            self.config = value
        elif key == "messages":
            self.messages = value
        elif key == "retrieved_memories":
            self.retrieved_memories = value
        elif key == "tool_outputs":
            self.tool_outputs = value
        elif key == "current_step":
            self.current_step = value
        else:
            raise KeyError(f"Chave '{key}' não encontrada")

    def get(self, key, default=None):
        """Implementa método get como dicionário."""
        try:
            return self[key]
        except KeyError:
            return default


class MemoryOperationResult(BaseModel):
    """Resultado de operação de memória."""

    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    memory_id: Optional[str] = Field(
        None, description="ID da memória (para operações de criação)"
    )
    content: Optional[str] = Field(None, description="Conteúdo da memória")
    memory_type: Optional[MemoryType] = Field(None, description="Tipo da memória")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    memories: Optional[List[MemoryResponse]] = Field(
        None, description="Lista de memórias (para operações de busca)"
    )


class ChatMessage(BaseModel):
    """Mensagem do chat."""

    role: str = Field(..., description="Papel da mensagem (user, assistant, system)")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp da mensagem"
    )


class ChatResponse(BaseModel):
    """Resposta do chat."""

    message: str = Field(..., description="Mensagem de resposta")
    memories_used: List[MemoryResponse] = Field(
        default_factory=list, description="Memórias usadas na resposta"
    )
    tools_called: List[str] = Field(
        default_factory=list, description="Ferramentas chamadas"
    )
    conversation_id: str = Field(..., description="ID da conversa")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp da resposta"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Tipo união para respostas de ferramentas
ToolResponse = Union[ToolSuccessResponse, ToolErrorResponse]
