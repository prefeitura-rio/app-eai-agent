import re
from typing import Dict, Any, Tuple, Union, Callable, Awaitable

from src.evaluations.core.llm_clients import AzureOpenAIClient, GeminiAIClient
from src.evaluations.core import prompt_judges

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

    @eval_method(name="conversational_reasoning", turns="multiple")
    async def conversational_reasoning(
        self, agent_response: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia o raciocínio com base em uma transcrição completa."""
        prompt = prompt_judges.FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT.format(
            golden_summary=task.get("golden_summary", ""), transcript=agent_response
        )
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": judgement_response,
        }

    @eval_method(name="conversational_memory", turns="multiple")
    async def conversational_memory(
        self, agent_response: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a memória com base em uma transcrição completa."""
        prompt = prompt_judges.FINAL_MEMORY_JUDGEMENT_PROMPT.format(
            golden_summary=task.get("golden_summary", ""), transcript=agent_response
        )
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": judgement_response,
        }

    @eval_method(name="semantic_correctness", turns="one")
    async def semantic_correctness(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a correção semântica de uma única resposta."""
        prompt = prompt_judges.SEMANTIC_CORRECTNESS_PROMPT.format(
            output=agent_response.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": judgement_response,
        }

    @eval_method(name="persona_adherence", turns="one")
    async def persona_adherence(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a aderência à persona de uma única resposta."""
        prompt = prompt_judges.PERSONA_ADHERENCE_PROMPT.format(
            output=agent_response.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": judgement_response,
        }
