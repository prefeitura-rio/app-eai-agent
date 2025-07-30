import asyncio
import json
import re
from typing import Dict, Any, List, Union, Callable, Awaitable, Tuple

from src.evaluations.core.llm_clients import (
    AzureOpenAIClient,
    GeminiAIClient,
    AgentConversationManager,
)
from src.evaluations.core import prompt_judges
import logging

logger = logging.getLogger(__name__)


_EVAL_METHODS_REGISTRY: Dict[str, Dict[str, Any]] = {}
JUDGE_STOP_SIGNAL = "EVALUATION_CONCLUDED"


def _extract_evaluation(response: str) -> Tuple[float, str]:
    """Extrai score e reasoning de uma string formatada."""
    score_match = re.search(r"Score:\s*([0-9.]+)", response, re.IGNORECASE)
    reasoning_match = re.search(r"Reasoning:\s*(.*)", response, re.DOTALL)

    score = float(score_match.group(1)) if score_match else 0.0
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    return score, reasoning


def eval_method(name: str, turns: str) -> Callable:
    """
    Decorador para registrar um método de avaliação.

    Args:
        name (str): O nome único da métrica.
        turns (str): O tipo de interação necessária: "one" ou "multiple".
    """
    if turns not in ["one", "multiple"]:
        raise ValueError("O parâmetro 'turns' deve ser 'one' ou 'multiple'.")

    def decorator(func: Callable[..., Awaitable[Dict[str, Any]]]) -> Callable:
        _EVAL_METHODS_REGISTRY[name] = {"func": func, "turns": turns}
        return func

    return decorator


class Evals:
    def __init__(self, judge_client: Union[AzureOpenAIClient, GeminiAIClient]):
        self.judge_client = judge_client

    @eval_method(name="conversational_reasoning", turns="multiple")
    async def evaluate_conversational_reasoning(
        self, conversation_manager: AgentConversationManager, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        task_id = task.get("id")
        logger.info(
            f"--- Iniciando avaliação 'conversational_reasoning' para a tarefa: {task_id} ---"
        )

        conversation_history = []
        judge_context = task.get("judge_context", "Nenhum contexto fornecido.")
        golden_summary = task.get("golden_response_summary", "")
        current_message_from_judge = task.get("prompt")
        transcript = []
        max_turns = 10
        last_agent_response = {}

        final_score = 0.0
        final_reasoning = (
            "Evaluation did not conclude properly (e.g., max turns reached)."
        )
        raw_final_judgement = ""

        for turn in range(max_turns):
            logger.info(
                f"[{task_id}][Turno {turn + 1}/{max_turns}] Enviando para o agente: '{current_message_from_judge}'"
            )
            if not current_message_from_judge:
                logger.warning(
                    f"[{task_id}] A mensagem do juiz está vazia. Encerrando a avaliação."
                )
                break

            agent_response = await conversation_manager.send_message(
                current_message_from_judge
            )
            last_agent_response = agent_response
            agent_output = agent_response.get("output", "Nenhuma resposta do agente.")
            logger.info(
                f"[{task_id}][Turno {turn + 1}] Agente respondeu: '{agent_output}'"
            )

            turn_data = {
                "turn": turn + 1,
                "judge_message": current_message_from_judge,
                "agent_response": agent_output,
                "agent_response_raw": agent_response,
            }
            transcript.append(turn_data)
            conversation_history.append(
                f"Turno {turn+1} - Juiz: {current_message_from_judge}\nTurno {turn+1} - Agente: {agent_output}"
            )

            history_str = "\n".join(conversation_history)
            prompt_for_judge = prompt_judges.CONVERSATIONAL_JUDGE_PROMPT.format(
                judge_context=judge_context,
                golden_summary=golden_summary,
                conversation_history=history_str,
                stop_signal=JUDGE_STOP_SIGNAL,
            )

            logger.info(
                f"[{task_id}][Turno {turn + 1}] Solicitando próxima ação/veredito do juiz."
            )
            judge_response = await self.judge_client.execute(prompt_for_judge)
            logger.info(
                f"[{task_id}][Turno {turn + 1}] Juiz respondeu: '{judge_response}'"
            )

            if JUDGE_STOP_SIGNAL in judge_response:
                logger.info(
                    f"[{task_id}] Sinal de parada detectado. Extraindo avaliação final."
                )
                raw_final_judgement = judge_response
                final_score, final_reasoning = _extract_evaluation(judge_response)
                break

            current_message_from_judge = judge_response
            logger.info(
                f"[{task_id}] Nenhum sinal de parada detectado. Continuando a conversa."
            )

        logger.info(
            f"--- Finalizada avaliação 'conversational_reasoning' para a tarefa: {task_id} ---"
        )

        return {
            "score": final_score,
            "annotations": {
                "reasoning": final_reasoning,
                "transcript": transcript,
                "raw_final_judgement": raw_final_judgement,
            },
            "last_agent_response": last_agent_response,
        }

    @eval_method(name="semantic_correctness", turns="one")
    async def evaluate_semantic_correctness(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = prompt_judges.SEMANTIC_CORRECTNESS_PROMPT.format(
            output=agent_response.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        score, reasoning = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": {
                "reasoning": reasoning,
                "raw_response": judgement_response,
            },
            "last_agent_response": agent_response,
        }

    @eval_method(name="persona_adherence", turns="one")
    async def evaluate_persona_adherence(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = prompt_judges.PERSONA_ADHERENCE_PROMPT.format(
            output=agent_response.get("output", ""), task=task
        )
        judgement_response = await self.judge_client.execute(prompt)
        score, reasoning = _extract_evaluation(judgement_response)
        return {
            "score": score,
            "annotations": {
                "reasoning": reasoning,
                "raw_response": judgement_response,
            },
            "last_agent_response": agent_response,
        }

    async def run(
        self,
        metrics_to_run: List[str],
        conversation_manager: AgentConversationManager,
        task: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        all_eval_results = []

        metrics_by_turns: Dict[str, List[str]] = {"one": [], "multiple": []}
        for m in metrics_to_run:
            turn_type = _EVAL_METHODS_REGISTRY.get(m, {}).get("turns")
            if turn_type:
                metrics_by_turns[turn_type].append(m)

        if metrics_by_turns["multiple"]:
            metric_name = metrics_by_turns["multiple"][0]
            eval_func = _EVAL_METHODS_REGISTRY[metric_name]["func"]
            result = await eval_func(self, conversation_manager, task)

            if isinstance(result, Exception):
                all_eval_results.append(
                    {
                        "eval_name": metric_name,
                        "score": 0.0,
                        "annotations": {"error": str(result)},
                        "last_agent_response": {},
                        "error": True,
                    }
                )
            else:
                all_eval_results.append(
                    {"eval_name": metric_name, **result, "error": False}
                )

        elif metrics_by_turns["one"]:
            initial_prompt = task.get("prompt")
            if not initial_prompt:
                raise ValueError(
                    "A tarefa não contém um 'prompt' para avaliação de turno único."
                )

            agent_response = await conversation_manager.send_message(initial_prompt)

            one_turn_coroutines = [
                _EVAL_METHODS_REGISTRY[m]["func"](self, agent_response, task)
                for m in metrics_by_turns["one"]
            ]
            results = await asyncio.gather(*one_turn_coroutines, return_exceptions=True)
            for i, metric_name in enumerate(metrics_by_turns["one"]):
                res = results[i]
                if isinstance(res, Exception):
                    all_eval_results.append(
                        {
                            "eval_name": metric_name,
                            "score": 0.0,
                            "annotations": {"error": str(res)},
                            "last_agent_response": agent_response,
                            "error": True,
                        }
                    )
                else:
                    all_eval_results.append(
                        {"eval_name": metric_name, **res, "error": False}
                    )

        return all_eval_results
