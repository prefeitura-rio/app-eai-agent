# -*- coding: utf-8 -*-
"""
EAI Evaluation Framework (`eval`)

Este pacote fornece um conjunto de ferramentas modulares e extensíveis para
conduzir avaliações complexas de agentes de IA.
"""

from src.evaluations.core.eval.conversation import ConversationHandler
from src.evaluations.core.eval.dataloader import DataLoader
from src.evaluations.core.eval.evaluators.base import BaseEvaluator
from src.evaluations.core.eval.llm_clients import (
    AgentConversationManager,
    AzureOpenAIClient,
    BaseJudgeClient,
    GeminiAIClient,
)
from src.evaluations.core.eval.runner import AsyncExperimentRunner
from src.evaluations.core.eval.schemas import (
    AgentResponse,
    ConversationTurn,
    EvaluationResult,
    EvaluationTask,
    MultiTurnContext,
    OneTurnAnalysis,
    MultiTurnAnalysis,
    ReasoningStep,
    RunResult,
)

__all__ = [
    "ConversationHandler",
    "DataLoader",
    "BaseEvaluator",
    "AgentConversationManager",
    "AzureOpenAIClient",
    "BaseJudgeClient",
    "GeminiAIClient",
    "AsyncExperimentRunner",
    "AgentResponse",
    "ConversationTurn",
    "EvaluationResult",
    "EvaluationTask",
    "MultiTurnContext",
    "OneTurnAnalysis",
    "MultiTurnAnalysis",
    "ReasoningStep",
    "RunResult",
]
