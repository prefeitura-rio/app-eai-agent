import ast
import re
from typing import Dict, Any, Tuple, Union, Callable, Awaitable, List

from src.evaluations.core.llm_clients import (
    AzureOpenAIClient,
    GeminiAIClient,
    AgentConversationManager,
)
from src.evaluations.core import prompt_judges

# from src.evaluations.core.utils import extract_answer_text, extract_links_from_text, parse_golden_links
from src.evaluations.letta.phoenix.training_dataset.evaluators import (
    get_answer_links,
    match_golden_link,
)
from src.utils.log import logger


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
    """Contêiner para métodos de avaliação puros.
    Input contex:
    task: colunas definidas no dataloader (id_col, prompt_col, metadata_cols)
    multi: agent_response
        transcript List[dict]
        conversation_history[str]
    one:   agent_response
        output[str]
        messages List[dict]
    """

    def __init__(self, judge_client: Union[AzureOpenAIClient, GeminiAIClient]):
        self.judge_client = judge_client

    async def _get_llm_judgement(
        self, prompt_template: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Formata um prompt, executa-o contra o cliente juiz e extrai o resultado.
        """
        prompt = prompt_template.format(**kwargs)
        # logger.info(prompt)
        judgement_response = await self.judge_client.execute(prompt)
        score = _extract_evaluation(judgement_response)
        return {"score": score, "annotations": judgement_response}

    @eval_method(name="conversational_reasoning", turns="multiple")
    async def conversational_reasoning(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia o raciocínio com base em uma transcrição completa."""
        return await self._get_llm_judgement(
            prompt_judges.FINAL_CONVERSATIONAL_JUDGEMENT_PROMPT,
            agent_response=agent_response,
            task=task,
        )

    @eval_method(name="conversational_memory", turns="multiple")
    async def conversational_memory(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a memória com base em uma transcrição completa."""
        return await self._get_llm_judgement(
            prompt_judges.FINAL_MEMORY_JUDGEMENT_PROMPT,
            agent_response=agent_response,
            task=task,
        )

    @eval_method(name="semantic_correctness", turns="one")
    async def semantic_correctness(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a correção semântica de uma única resposta."""
        return await self._get_llm_judgement(
            prompt_judges.SEMANTIC_CORRECTNESS_PROMPT,
            agent_response=agent_response,
            task=task,
        )

    @eval_method(name="persona_adherence", turns="one")
    async def persona_adherence(
        self, agent_response: Dict[str, Any], task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Avalia a aderência à persona de uma única resposta."""
        return await self._get_llm_judgement(
            prompt_judges.PERSONA_ADHERENCE_PROMPT,
            agent_response=agent_response,
            task=task,
        )

    # @eval_method(name="golden_equipment", turns="multiple")
    # async def golden_equipment(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Tuple[bool, str]:
    #     """Avalia se o equipamento correto foi chamado na resposta."""
    #     return await self._get_llm_judgement(
    #         prompt_judges.GOLDEN_EQUIPMENT_PROMPT,
    #         golden_summary=task.get("golden_response_multiple_shot", ""),
    #         transcript=agent_response,
    #     )

    # @eval_method(name="answer_completeness", turns="one")
    # async def answer_completeness(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Dict[str, Any]:
    #     """Avalia a completude da resposta de uma única resposta."""
    #     return await self._get_llm_judgement(
    #         prompt_judges.ANSWER_COMPLETENESS_PROMPT,
    #         output=agent_response.get("output", ""),
    #         task=task,
    #     )

    # @eval_method(name="answer_addressing", turns="one")
    # async def answer_addressing(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Dict[str, Any]:
    #     """Avalia se a resposta aborda adequadamente a pergunta."""
    #     return await self._get_llm_judgement(
    #         prompt_judges.ANSWER_ADDRESSING_PROMPT,
    #         output=agent_response.get("output", ""),
    #         task=task,
    #     )

    # @eval_method(name="clarity", turns="one")
    # async def clarity(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Dict[str, Any]:
    #     """Avalia a clareza da resposta de uma única resposta."""
    #     return await self._get_llm_judgement(
    #         prompt_judges.CLARITY_PROMPT,
    #         output=agent_response.get("output", ""),
    #         task=task,
    #     )

    # @eval_method(name="activate_search", turns="one")
    # async def activate_search(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Tuple[bool, str]:
    #     """Avalia se a busca foi ativada corretamente."""
    #     grouped = agent_response.get("output", "").get("grouped", {})
    #     tool_msgs = grouped.get("tool_return_messages", [])

    #     SEARCH_TOOL_NAMES = [
    #         # "public_services_grounded_search",
    #         "google_search",
    #         "equipments_instructions",
    #         "equipments_by_address",
    #     ]

    #     activated = {
    #         msg.get("name") for msg in tool_msgs if msg.get("name") in SEARCH_TOOL_NAMES
    #     }
    #     explanation = f"Activated tools: {list(activated)}"

    #     return len(activated) > 0, explanation

    # @eval_method(name="golden_link_in_tool_calling", turns="one")
    # async def golden_link_in_tool_calling(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Tuple[bool, Dict[str, Any]]:
    #     """Avalia se o link correto foi chamado na ferramenta."""
    #     golden_field = agent_response.get("metadata", {}).get("golden_links_list", "")
    #     golden_links = parse_golden_links(golden_field)

    #     answer_links = agent_response.get("agent_output").get(
    #         "fontes"
    #     ) or get_answer_links(output=agent_response)

    #     if agent_response.get("agent_output", {}).get("resposta_gpt"):
    #         answer_links = [
    #             {"uri": link, "url": link} for link in ast.literal_eval(answer_links)
    #         ]

    #     if not answer_links or not golden_links:
    #         return False, {
    #             "reason": "No links found in the answer or no golden links provided"
    #         }

    #     answer_links, count = match_golden_link(
    #         answer_links=answer_links, golden_links=golden_links
    #     )

    #     explanation = {
    #         "golden_links": golden_links,
    #         "answer_links": answer_links,
    #         "number_of_matches": count,
    #     }

    #     return count > 0, explanation

    # @eval_method(name="golden_link_in_answer", turns="one")
    # async def golden_link_in_answer(
    #     self, agent_response: Dict[str, Any], task: Dict[str, Any]
    # ) -> Tuple[bool, Dict[str, Any]]:
    #     """Avalia se o link correto foi incluído na resposta."""
    #     golden_field = agent_response.get("metadata", {}).get("golden_links_list", "")
    #     golden_links = parse_golden_links(golden_field)
    #     resposta = extract_answer_text(agent_response)
    #     raw_links = extract_links_from_text(resposta)

    #     if not raw_links or not golden_links:
    #         return False, {
    #             "reason": "No links found in the answer or no golden links provided"
    #         }

    #     unique_links = list(
    #         dict.fromkeys([link for link in raw_links if isinstance(link, str)])
    #     )

    #     link_dicts = [{"url": url} for url in unique_links]

    #     tool_calling_links = get_answer_links(agent_response)
    #     url_to_uri = {l.get("url"): l.get("uri") for l in tool_calling_links}

    #     enriched_links = [
    #         {"url": l.get("url"), "uri": url_to_uri.get(l.get("url"))}
    #         for l in link_dicts
    #         if l.get("url") in url_to_uri
    #     ]
    #     enriched_links, count = match_golden_link(
    #         answer_links=enriched_links, golden_links=golden_links
    #     )

    #     explanation = {
    #         "golden_links": golden_links,
    #         "answer_links": enriched_links,
    #         "number_of_matches": count,
    #     }

    #     return count > 0, explanation


class ConversationHandler:
    """
    Gerencia a condução de uma única conversa entre o juiz e o agente.
    """

    def __init__(self, conv_manager: AgentConversationManager, evaluation_suite: Evals):
        self.conv_manager = conv_manager
        self.evaluation_suite = evaluation_suite

    async def conduct(
        self, task: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any], list]:
        """
        Conduz uma conversa multi-turno, guiada por um juiz, e retorna a transcrição.
        """
        JUDGE_STOP_SIGNAL = "EVALUATION_CONCLUDED"

        transcript, history = [], []
        current_message = task.get("prompt")
        last_response = {}
        for turn in range(15):  # Hardcoded limit
            agent_res = await self.conv_manager.send_message(current_message)
            last_response = agent_res
            transcript.append(
                {
                    "turn": turn + 1,
                    "judge_message": current_message,
                    "agent_response": agent_res.get("output"),
                    "reasoning_trace": agent_res.get("messages"),
                }
            )
            history.append(
                f"Turno {turn+1} - User: {current_message}\nTurno {turn+1} - Agente: {agent_res.get('output')}"
            )

            prompt_for_judge = prompt_judges.CONVERSATIONAL_JUDGE_PROMPT.format(
                task=task,
                agent_response={"conversation_history": "\n".join(history)},
                stop_signal=JUDGE_STOP_SIGNAL,
            )
            judge_res = await self.evaluation_suite.judge_client.execute(
                prompt_for_judge
            )
            if JUDGE_STOP_SIGNAL in judge_res:
                history.append(f"Turno {turn+2} - User: {judge_res}")
                transcript.append(
                    {
                        "turn": turn + 2,
                        "judge_message": judge_res,
                        "agent_response": None,
                        "reasoning_trace": None,
                    }
                )
                break
            current_message = judge_res

        return transcript, last_response, history
