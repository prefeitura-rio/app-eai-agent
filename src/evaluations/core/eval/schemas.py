# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class ReasoningStep(BaseModel):
    """Representa um único passo na cadeia de pensamento de um agente."""

    message_type: str
    content: Union[str, Dict[str, Any], None]


class ConversationTurn(BaseModel):
    """Representa um turno completo em uma conversa multi-turno."""

    turn: int
    judge_message: str
    agent_response: Optional[str] = None
    reasoning_trace: Optional[List[ReasoningStep]] = None


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
    Estrutura a resposta de uma interação com o agente.
    """

    output: Optional[str] = None
    messages: Optional[List[ReasoningStep]] = None
    has_error: bool = False
    error_message: Optional[str] = None


class ConversationOutput(BaseModel):
    """
    Estrutura a saída de um avaliador do tipo 'conversation', contendo
    todos os artefatos gerados durante o diálogo.
    """

    transcript: List[ConversationTurn] = []
    conversation_history: str = ""
    duration_seconds: float = 0.0
    has_error: bool = False
    error_message: Optional[str] = None


class EvaluationContext(BaseModel):
    """Contém todo o contexto necessário para um avaliador executar."""

    task: EvaluationTask
    one_turn_response: AgentResponse
    multi_turn_output: Optional[ConversationOutput] = None


class EvaluationResult(BaseModel):
    """
    Define a saída padronizada para qualquer método de avaliação, garantindo
    consistência nos resultados.
    """

    score: Optional[float] = None
    annotations: str
    has_error: bool = False
    error_message: Optional[str] = None


class RunResult(BaseModel):
    """
    Define a estrutura completa do resultado para um único 'run' (tarefa)
    dentro de um experimento.
    """

    duration_seconds: float
    task_data: EvaluationTask
    one_turn_response: AgentResponse
    multi_turn_output: Optional[ConversationOutput] = None
    evaluations: List[Dict[str, Any]] = []