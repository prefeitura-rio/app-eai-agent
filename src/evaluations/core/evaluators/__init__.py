# -*- coding: utf-8 -*-
"""
Este pacote contém as classes de avaliação modulares.

Cada avaliador herda de BaseEvaluator e encapsula a lógica para uma
única métrica de avaliação, juntamente com seu próprio template de prompt.
Isso torna o sistema extensível, permitindo que novas métricas sejam
adicionadas sem modificar o código central do runner.
"""

from src.evaluations.core.evaluators.base import BaseEvaluator
from src.evaluations.core.evaluators.conversational_memory import (
    ConversationalMemoryEvaluator,
)
from src.evaluations.core.evaluators.conversational_reasoning import (
    ConversationalReasoningEvaluator,
)
from src.evaluations.core.evaluators.persona_adherence import PersonaAdherenceEvaluator
from src.evaluations.core.evaluators.semantic_correctness import (
    SemanticCorrectnessEvaluator,
)

__all__ = [
    "BaseEvaluator",
    "ConversationalMemoryEvaluator",
    "ConversationalReasoningEvaluator",
    "PersonaAdherenceEvaluator",
    "SemanticCorrectnessEvaluator",
]
