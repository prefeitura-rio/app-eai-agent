# -*- coding: utf-8 -*-
"""
Este pacote contém as classes de avaliação modulares.

Cada avaliador herda de BaseEvaluator e encapsula a lógica para uma
única métrica de avaliação, juntamente com seu próprio template de prompt.
Isso torna o sistema extensível, permitindo que novas métricas sejam
adicionadas sem modificar o código central do runner.
"""

from .batman_llm_guided_conversation import BatmanLLMGuidedConversation
from .conversational_memory import (
    ConversationalMemoryEvaluator,
)
from .conversational_reasoning import (
    ConversationalReasoningEvaluator,
)
from .persona_adherence import (
    PersonaAdherenceEvaluator,
)
from .semantic_correctness import (
    SemanticCorrectnessEvaluator,
)

__all__ = [
    "BatmanLLMGuidedConversation",
    "ConversationalMemoryEvaluator",
    "ConversationalReasoningEvaluator",
    "PersonaAdherenceEvaluator",
    "SemanticCorrectnessEvaluator",
]
