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
    agent_response: Optional[str]
    reasoning_trace: Optional[List[ReasoningStep]]


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

    output: Optional[str]
    messages: Optional[List[ReasoningStep]]


class MultiTurnContext(BaseModel):
    """Contém todo o contexto de uma conversa multi-turno para avaliação."""

    conversation_history: str
    transcript: List[ConversationTurn]


class EvaluationResult(BaseModel):
    """
    Define a saída padronizada para qualquer método de avaliação, garantindo
    consistência nos resultados.
    """

    score: Optional[float]
    annotations: str
    has_error: bool = False
    error_message: Optional[str] = None


class OneTurnAnalysis(BaseModel):
    """Estrutura a análise completa para uma avaliação de turno único."""

    agent_response: Optional[str]
    reasoning_trace: Optional[List[ReasoningStep]]
    evaluations: List[Dict[str, Any]]  # Mantido como Dict por flexibilidade no runner


class MultiTurnAnalysis(BaseModel):
    """Estrutura a análise completa para uma avaliação multi-turno."""

    final_agent_response: Optional[str]
    conversation_transcript: Optional[List[ConversationTurn]]
    evaluations: List[Dict[str, Any]]  # Mantido como Dict por flexibilidade no runner


class RunResult(BaseModel):
    """
    Define a estrutura completa do resultado para um único 'run' (tarefa)
    dentro de um experimento.
    """

    duration_seconds: float
    task_data: EvaluationTask
    one_turn_analysis: OneTurnAnalysis
    multi_turn_analysis: MultiTurnAnalysis
    error: Optional[str] = None
