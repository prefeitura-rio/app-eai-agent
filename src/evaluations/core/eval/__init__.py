# -*- coding: utf-8 -*-
"""
EAI Evaluation Framework (`eval`)

Este pacote fornece um conjunto de ferramentas modulares e extensíveis para
conduzir avaliações complexas de agentes de IA.
"""

from src.evaluations.core.eval.dataloader import DataLoader
from src.evaluations.core.eval.evaluators.base import (
    BaseEvaluator,
    BaseConversationEvaluator,
    BaseOneTurnEvaluator,
    BaseMultipleTurnEvaluator,
)
from src.evaluations.core.eval.llm_clients import (
    EAIConversationManager,
    AzureOpenAIClient,
    BaseJudgeClient,
    GeminiAIClient,
)
from src.evaluations.core.eval.runner.orchestrator import AsyncExperimentRunner
from src.evaluations.core.eval.schemas import (
    AgentResponse,
    ConversationTurn,
    EvaluationResult,
    EvaluationTask,
    MultiTurnEvaluationInput,
    OneTurnAnalysis,
    MultiTurnAnalysis,
    ReasoningStep,
    TaskOutput,
    ConversationOutput,
)

__all__ = [
    "DataLoader",
    "BaseEvaluator",
    "BaseConversationEvaluator",
    "BaseOneTurnEvaluator",
    "BaseMultipleTurnEvaluator",
    "EAIConversationManager",
    "AzureOpenAIClient",
    "BaseJudgeClient",
    "GeminiAIClient",
    "AsyncExperimentRunner",
    "AgentResponse",
    "ConversationTurn",
    "EvaluationResult",
    "EvaluationTask",
    "MultiTurnEvaluationInput",
    "OneTurnAnalysis",
    "MultiTurnAnalysis",
    "ReasoningStep",
    "TaskOutput",
    "ConversationOutput",
]
