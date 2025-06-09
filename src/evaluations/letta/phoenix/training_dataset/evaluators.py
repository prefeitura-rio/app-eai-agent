import pandas as pd
import asyncio
from typing import Tuple, Dict, Any, Optional, Union
from src.evaluations.letta.agents.final_response import (
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    CLARITY_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    GOLD_STANDARD_SIMILARITY_LLM_JUDGE_PROMPT,
    GROUNDEDNESS_LLM_JUDGE_PROMPT,
    LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
    SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
    WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.router import (
    SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
    TOOL_CALLING_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.search_tools import (
    SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
)

from phoenix.experiments.evaluators import create_evaluator

def _get_experiment_functions():
    from src.evaluations.letta.phoenix.training_dataset.experiments import (
        empty_agent_core_memory,
        experiment_eval,
        tool_returns,
    )
    return empty_agent_core_memory, experiment_eval, tool_returns


async def eval_binary(prompt: str, rails: list, input: Dict[str, Any], 
                      output: Dict[str, Any], extra_kwargs: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """Função auxiliar assíncrona para realizar avaliações binárias"""
    extra_kwargs = extra_kwargs or {}
    
    _, experiment_eval, _ = _get_experiment_functions()
    
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=prompt,
        rails=rails,
        **extra_kwargs,
    )

    return response


@create_evaluator(name="Answer Completeness", kind="LLM")
async def experiment_eval_answer_completeness(input: Dict[str, Any], 
                                             output: Dict[str, Any], 
                                             expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia se a resposta está completa"""
    rails_answer_completeness = ["complete", "incomplete"]

    return await eval_binary(
        ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails_answer_completeness,
        input,
        output,
    )


@create_evaluator(name="Clarity", kind="LLM")
async def experiment_eval_clarity(input: Dict[str, Any], 
                                 output: Dict[str, Any], 
                                 expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a clareza da resposta"""
    rails_clarity = ["clear", "unclear"]

    return await eval_binary(
        CLARITY_LLM_JUDGE_PROMPT,
        rails_clarity,
        input,
        output,
    )


@create_evaluator(name="Similarity Ideal Response", kind="LLM")
async def experiment_eval_gold_standard_similarity(input: Dict[str, Any], 
                                                  output: Dict[str, Any], 
                                                  expected: Dict[str, Any]) -> Union[float, bool, Tuple[bool, str]]:
    """Avalia a similaridade com a resposta ideal"""
    rails_gold_standard_similarity = ["equivalent", "similar", "different"]
    mapping = {"equivalent": 1, "similar": 0.5, "different": 0}

    _, experiment_eval, _ = _get_experiment_functions()

    response = await experiment_eval(
        input=input,
        output=output,
        prompt=GOLD_STANDARD_SIMILARITY_LLM_JUDGE_PROMPT,
        rails=rails_gold_standard_similarity,
        expected=expected,
    )

    if isinstance(response, tuple) and len(response) >= 1:
        result, explanation = response
        if isinstance(result, bool) and not result:
            return result, explanation
    
    label = response[0] if isinstance(response, tuple) else response
    
    if isinstance(label, str) and label in mapping:
        return mapping[label], "Avaliação de similaridade concluída"
    
    return False, "Não foi possível determinar a similaridade"


@create_evaluator(name="Emergency Handling", kind="LLM")
async def experiment_eval_emergency_handling_compliance(input: Dict[str, Any], 
                                                       output: Dict[str, Any], 
                                                       expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a conformidade com o tratamento de emergências"""
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_emergency_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Entity Presence", kind="LLM")
async def experiment_eval_entity_presence(input: Dict[str, Any], 
                                         output: Dict[str, Any], 
                                         expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a presença de entidades na resposta"""
    rails_entity_presence = ["entities_present", "entities_missing"]

    return await eval_binary(
        ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails_entity_presence,
        input,
        output,
    )


@create_evaluator(name="Feedback Handling", kind="LLM")
async def experiment_eval_feedback_handling_compliance(input: Dict[str, Any], 
                                                      output: Dict[str, Any], 
                                                      expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a conformidade com o tratamento de feedback"""
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_feedback_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Location Policy", kind="LLM")
async def experiment_eval_location_policy_compliance(input: Dict[str, Any], 
                                                    output: Dict[str, Any], 
                                                    expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a conformidade com políticas de localização"""
    rails_location_policy_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails_location_policy_compliance,
        input,
        output,
    )


@create_evaluator(name="Security and Privacy", kind="LLM")
async def experiment_eval_security_privacy_compliance(input: Dict[str, Any], 
                                                     output: Dict[str, Any], 
                                                     expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a conformidade com segurança e privacidade"""
    rails_security_privacy_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails_security_privacy_compliance,
        input,
        output,
    )


@create_evaluator(name="Whatsapp Format", kind="LLM")
async def experiment_eval_whatsapp_formatting_compliance(input: Dict[str, Any], 
                                                        output: Dict[str, Any], 
                                                        expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a conformidade com formatação do WhatsApp"""
    rails_whatsapp_formatting_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails_whatsapp_formatting_compliance,
        input,
        output,
    )


@create_evaluator(name="Groundness", kind="LLM")
async def experiment_eval_groundedness(input: Dict[str, Any], 
                                      output: Dict[str, Any], 
                                      expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a fundamentação da resposta nos dados disponíveis"""
    rails_groundedness = ["based", "unfounded"]

    empty_agent_core_memory, _, tool_returns = _get_experiment_functions()

    return await eval_binary(
        GROUNDEDNESS_LLM_JUDGE_PROMPT,
        rails_groundedness,
        input,
        output,
        extra_kwargs={
            "core_memory": empty_agent_core_memory(),
            "search_tool_results": tool_returns(output),
        },
    )


@create_evaluator(name="Search Result Coverage", kind="LLM")
async def experiment_eval_search_result_coverage(input: Dict[str, Any], 
                                               output: Dict[str, Any], 
                                               expected: Dict[str, Any]) -> Tuple[bool, str]:
    """Avalia a cobertura dos resultados de busca na resposta"""
    rails_search_result_coverage = ["covers", "uncovers"]

    _, _, tool_returns = _get_experiment_functions()

    return await eval_binary(
        SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
        rails_search_result_coverage,
        input,
        output,
        extra_kwargs={
            "search_tool_results": tool_returns(output),
        },
    )


@create_evaluator(name="Tool Calling", kind="LLM")
async def experiment_eval_tool_calling(input: Dict[str, Any], 
                                      output: Dict[str, Any], 
                                      expected: Dict[str, Any]) -> Union[float, bool, Tuple[bool, str]]:
    """Avalia a eficácia da chamada de ferramentas"""
    from src.evaluations.letta.phoenix.utils import get_system_prompt
    
    tool_definitions = get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

    rails_tool_calling = ["correct", "incorrect"]
    results = []

    _, experiment_eval, _ = _get_experiment_functions()

    for tool_call_details in output.get("tool_call_messages", []):
        tool_call = tool_call_details.get("tool_call", {})
        if tool_call.get("name") in ("typesense_search", "google_search"):
            response = await experiment_eval(
                input=input,
                output=output,
                prompt=TOOL_CALLING_LLM_JUDGE_PROMPT.replace(
                    "{tool_definitions}", tool_definitions
                ),
                rails=rails_tool_calling,
                tool_call=tool_call,
            )

            if isinstance(response, tuple) and len(response) >= 1:
                label = response[0]
                result = 1 if label is True or label == rails_tool_calling[0] else 0
            else:
                result = 0
                
            results.append(result)

    if not results:
        return False, "Nenhuma chamada de ferramenta para avaliar"
    
    avg_result = sum(results) / len(results)
    return avg_result, f"Média de eficácia: {avg_result:.2f}"


@create_evaluator(name="Search Tool Abstractness", kind="LLM")
async def experiment_eval_search_query_effectiveness(input: Dict[str, Any], 
                                                   output: Dict[str, Any], 
                                                   expected: Dict[str, Any]) -> Union[float, bool, Tuple[bool, str]]:
    """Avalia a eficácia das consultas de busca"""
    from src.evaluations.letta.phoenix.utils import extrair_query
    
    rails_search_query_effectiveness = ["effective", "innefective"]
    results = []

    _, experiment_eval, _ = _get_experiment_functions()

    if output:
        for tool_call_details in output.get("tool_call_messages", []):
            tool_call = tool_call_details.get("tool_call", {})
            if tool_call.get("name") in ("typesense_search", "google_search"):
                query = extrair_query(tool_call.get("arguments", ""))
                response = await experiment_eval(
                    input=input,
                    output=output,
                    prompt=SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
                    rails=rails_search_query_effectiveness,
                    search_tool_query=query,
                )

                if isinstance(response, tuple) and len(response) >= 1:
                    label = response[0]
                    result = 1 if label is True or label == rails_search_query_effectiveness[0] else 0
                else:
                    result = 0
                    
                results.append(result)
    
    if not results:
        return False, "Nenhuma consulta de busca para avaliar"
    
    avg_result = sum(results) / len(results)
    return avg_result, f"Média de eficácia: {avg_result:.2f}"
