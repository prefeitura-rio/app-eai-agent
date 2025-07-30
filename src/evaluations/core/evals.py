import re
from typing import Dict, Any, Tuple, Union, Callable, Awaitable

from src.evaluations.core.llm_clients import (
    AzureOpenAIClient,
    GeminiAIClient,
    AgentConversationManager,
)
from src.evaluations.core import prompt_judges
from typing import Dict, Any, Tuple, List

import logging

logger = logging.getLogger(__name__)


_EVAL_METHODS_REGISTRY: Dict[str, Dict[str, Any]] = {}


def _extract_evaluation(response: str) -> float:
    """Extrai score e reasoning de uma string formatada."""
    score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
    score = float(score_match.group(1)) if score_match else 0.0
    return score


def eval_method(name: str, turns: str) -> Callable:
    """Decorador para registrar um método de avaliação e seu tipo."""
    if turns not in ["one", "multiple"]:
        raise ValueError("O parâmetro 'turns' deve ser 'one' ou 'multiple'.")

    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable:
        _EVAL_METHODS_REGISTRY[name] = {"func": func, "turns": turns}
        return func

    return decorator


class Evals:
    """Contêiner para métodos de avaliação puros."""

    def __init__(self, judge_client: Union[AzureOpenAIClient, GeminiAIClient]):
        self.judge_client = judge_client

    async def _get_llm_judgement(self, prompt_template: str, **kwargs) -> Dict[str, Any]:
        """
        Formata um prompt, executa-o contra o cliente juiz e extrai o resultado.
        """
        prompt = prompt_template.format(**kwargs)
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {"score": score, "annotations": judgement_response}

    @eval_method(name="conversational_reasoning", turns="multiple")
    async def conversational_reasoning(
        self, agent_response: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia o raciocínio com base em uma transcrição completa."""
        return await self._get_llm_judgement(
            prompt_judges.FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT,
            golden_summary=task.get("golden_summary", ""),
            transcript=agent_response,
        )

    @eval_method(name="conversational_memory", turns="multiple")
    async def conversational_memory(
        self, agent_response: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a memória com base em uma transcrição completa."""
        return await self._get_llm_judgement(
            prompt_judges.FINAL_MEMORY_JUDGEMENT_PROMPT,
            golden_summary=task.get("golden_summary", ""),
            transcript=agent_response,
        )

    @eval_method(name="semantic_correctness", turns="one")
    async def semantic_correctness(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a correção semântica de uma única resposta."""
        return await self._get_llm_judgement(
            prompt_judges.SEMANTIC_CORRECTNESS_PROMPT,
            output=agent_response.get("output", ""),
            task=task,
        )

    @eval_method(name="persona_adherence", turns="one")
    async def persona_adherence(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a aderência à persona de uma única resposta."""
        return await self._get_llm_judgement(
            prompt_judges.PERSONA_ADHERENCE_PROMPT,
            output=agent_response.get("output", ""),
            task=task,
        )


class ConversationHandler:
    """
    Gerencia a condução de uma única conversa entre o juiz e o agente.
    """

    def __init__(self, conv_manager: AgentConversationManager, evaluation_suite: Evals):
        self.conv_manager = conv_manager
        self.evaluation_suite = evaluation_suite

    async def conduct(
        self, task: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Conduz uma conversa multi-turno, guiada por um juiz, e retorna a transcrição.
        """
        JUDGE_STOP_SIGNAL = "EVALUATION_CONCLUDED"

        transcript, history = [], []
        current_message = task.get("prompt")
        last_response = {}
        for turn in range(10):  # Hardcoded limit
            agent_res = await self.conv_manager.send_message(current_message)
            last_response = agent_res
            transcript.append(
                {
                    "turn": turn + 1,
                    "judge_message": current_message,
                    "agent_response": agent_res.get("output"),
                    "agent_response_raw": agent_res.get("messages"),
                }
            )
            history.append(
                f"Turno {turn+1} - Juiz: {current_message}\nTurno {turn+1} - Agente: {agent_res.get('output')}"
            )

            prompt_for_judge = prompt_judges.CONVERSATIONAL_JUDGE_PROMPT.format(
                judge_context=task["judge_context"],
                conversation_history="\n".join(history),
                stop_signal=JUDGE_STOP_SIGNAL,
            )
            judge_res = await self.evaluation_suite.judge_client.execute(
                prompt_for_judge
            )
            if JUDGE_STOP_SIGNAL in judge_res:
                break
            current_message = judge_res
        return transcript, last_response
