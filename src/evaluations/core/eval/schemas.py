# -*- coding: utf-8 -*-
from pydantic import BaseModel, model_validator
from typing import List, Dict, Any, Optional, Union


class ReasoningStep(BaseModel):
    """Representa um único passo na cadeia de pensamento de um agente."""

    message_type: str
    content: Union[str, Dict[str, Any], None]


class ConversationTurn(BaseModel):
    """Representa um turno completo em uma conversa multi-turno."""

    turn: int
    user_message: str
    agent_message: Optional[str] = None
    agent_reasoning_trace: Optional[List[ReasoningStep]] = None


class EvaluationTask(BaseModel):
    """
    Define a estrutura de uma única tarefa de avaliação, garantindo que todos os
    dados necessários do dataset estejam presentes e tipados.
    """

    id: str
    prompt: str

    # Permite que outras colunas de metadados existam sem quebrar o modelo
    class Config:
        extra = "allow"


class AgentResponse(BaseModel):
    """
    Estrutura a resposta de uma interação com o agente, seja de um ou múltiplos turnos.
    """

    message: Optional[str] = None
    reasoning_trace: Optional[List[ReasoningStep]] = None


class MultiTurnEvaluationInput(BaseModel):
    """Contém todo o contexto de uma conversa multi-turno para avaliação."""

    conversation_history: str
    transcript: List[ConversationTurn]


class ConversationOutput(BaseModel):
    """
    Estrutura a saída de um avaliador do tipo 'conversation', contendo
    todos os artefatos gerados durante o diálogo.
    """

    transcript: List[ConversationTurn]
    final_agent_message_details: AgentResponse
    conversation_history: List[str]
    duration_seconds: float


class EvaluationResult(BaseModel):
    """
    Define a saída padronizada para qualquer método de avaliação, garantindo
    consistência nos resultados.
    """

    score: Optional[float] = None
    annotations: str
    has_error: bool = False
    error_message: Optional[str] = None


class OneTurnAnalysis(BaseModel):
    """Estrutura a análise completa para uma avaliação de turno único."""

    agent_message: Optional[str] = None
    agent_reasoning_trace: Optional[List[ReasoningStep]] = None
    evaluations: List[Dict[str, Any]] = []
    has_error: bool = False
    error_message: Optional[str] = None


class MultiTurnAnalysis(BaseModel):
    """Estrutura a análise completa para uma avaliação multi-turno."""

    final_agent_message: Optional[str] = None
    transcript: Optional[List[ConversationTurn]] = None
    evaluations: List[Dict[str, Any]] = []
    has_error: bool = False
    error_message: Optional[str] = None


class TaskOutput(BaseModel):
    """
    Define a estrutura completa do resultado para um único 'run' (tarefa)
    dentro de um experimento.
    """

    duration_seconds: float
    task_data: EvaluationTask
    one_turn_analysis: OneTurnAnalysis
    multi_turn_analysis: MultiTurnAnalysis


class PrecomputedResponseModel(BaseModel):
    """
    Define o schema esperado para cada entrada no arquivo de respostas pré-computadas,
    usado para validação estrutural.
    """

    id: str
    one_turn_agent_message: Optional[str] = None
    one_turn_reasoning_trace: Optional[List[ReasoningStep]] = None
    multi_turn_transcript: Optional[List[ConversationTurn]] = None

    @model_validator(mode="after")
    def check_at_least_one_response_present(self) -> "PrecomputedResponseModel":
        if not self.one_turn_agent_message and not self.multi_turn_transcript:
            raise ValueError(
                "Cada resposta pré-computada deve ter pelo menos 'one_turn_agent_message' ou 'multi_turn_transcript'."
            )
        return self