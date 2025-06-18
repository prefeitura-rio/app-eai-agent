import pandas as pd
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
    GOOD_RESPONSE_STANDARDS_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.router import (
    SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
    TOOL_CALLING_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.agents.search_tools import (
    SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
)

from src.evaluations.letta.phoenix.training_dataset.experiments import (
    empty_agent_core_memory,
    experiment_eval,
    tool_returns,
)

from src.evaluations.letta.phoenix.utils import extrair_query, get_system_prompt

from phoenix.experiments.evaluators import create_evaluator


async def eval_binary(prompt, rails, input, output, extra_kwargs=None):
    extra_kwargs = extra_kwargs or {}
    response = await experiment_eval(
        input=input,
        output=output,
        prompt=prompt,
        rails=rails,
        **extra_kwargs,
    )

    return response


@create_evaluator(name="Padrões de Boa Resposta", kind="LLM")
async def experiment_eval_good_response_standards(
    input, output, expected
) -> tuple | bool:
    rails_answer_completeness = ["meets_standards", "lacks_standards"]

    return await eval_binary(
        GOOD_RESPONSE_STANDARDS_LLM_JUDGE_PROMPT,
        rails_answer_completeness,
        input,
        output,
    )


@create_evaluator(name="Completude", kind="LLM")
async def experiment_eval_answer_completeness(input, output, expected) -> tuple | bool:
    rails_answer_completeness = ["answered", "unanswered"]

    return await eval_binary(
        ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails_answer_completeness,
        input,
        output,
    )


@create_evaluator(name="Clareza", kind="LLM")
async def experiment_eval_clarity(input, output, expected) -> tuple | bool:
    rails_clarity = ["clear", "unclear"]

    return await eval_binary(
        CLARITY_LLM_JUDGE_PROMPT,
        rails_clarity,
        input,
        output,
    )


@create_evaluator(name="Similaridade com Resposta Ideal", kind="LLM")
async def experiment_eval_gold_standard_similarity(
    input, output, expected
) -> float | bool:
    rails_gold_standard_similarity = ["equivalent", "similar", "different"]
    mapping = {"equivalent": 1, "similar": 0.5, "different": 0}

    response = await experiment_eval(
        input=input,
        output=output,
        prompt=GOLD_STANDARD_SIMILARITY_LLM_JUDGE_PROMPT,
        rails=rails_gold_standard_similarity,
        expected=expected,
    )

    if not isinstance(response, bool):
        label = response.get("label")

        if isinstance(response, pd.Series):
            label = label.iloc[0]
        if isinstance(label, str) and label in mapping:
            return mapping[label]

    return False


@create_evaluator(name="Lidar com Emergências", kind="LLM")
async def experiment_eval_emergency_handling_compliance(
    input, output, expected
) -> tuple | bool:
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_emergency_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Presença de Entidades Chave", kind="LLM")
async def experiment_eval_entity_presence(input, output, expected) -> tuple | bool:
    rails_entity_presence = ["entities_present", "entities_missing"]

    return await eval_binary(
        ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails_entity_presence,
        input,
        output,
    )


@create_evaluator(name="Lidar com Feedback", kind="LLM")
async def experiment_eval_feedback_handling_compliance(
    input, output, expected
) -> tuple | bool:
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_feedback_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Política de Localização", kind="LLM")
async def experiment_eval_location_policy_compliance(
    input, output, expected
) -> tuple | bool:
    rails_location_policy_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails_location_policy_compliance,
        input,
        output,
    )


@create_evaluator(name="Segurança e Privacidade", kind="LLM")
async def experiment_eval_security_privacy_compliance(
    input, output, expected
) -> tuple | bool:
    rails_security_privacy_compliance = ["compliant", "non_compliant"]

    return await eval_binary(
        SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails_security_privacy_compliance,
        input,
        output,
    )


@create_evaluator(name="Formato WhatsApp", kind="LLM")
async def experiment_eval_whatsapp_formatting_compliance(
    input, output, expected
) -> tuple | bool:
    rails_whatsapp_formatting_compliance = ["compliant_format", "non_compliant_format"]

    return await eval_binary(
        WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails_whatsapp_formatting_compliance,
        input,
        output,
    )


@create_evaluator(name="Fundamentação", kind="LLM")
async def experiment_eval_groundedness(input, output, expected) -> tuple | bool:
    rails_groundedness = ["based", "unfounded"]

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


@create_evaluator(name="Cobertura dos Resultados da Busca", kind="LLM")
async def experiment_eval_search_result_coverage(
    input, output, expected
) -> tuple | bool:
    rails_search_result_coverage = ["covers", "uncovers"]

    return await eval_binary(
        SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
        rails_search_result_coverage,
        input,
        output,
        extra_kwargs={
            "search_tool_results": tool_returns(output),
        },
    )


@create_evaluator(name="Golden Link Aparece na Resposta Final", kind="LLM")
async def experiment_eval_golden_links_appear_final_answ(
    input, output, expected
) -> tuple | bool:

    if input in output:
        response = True
    else:
        response = False

    return response


@create_evaluator(name="Golden Link Aparece no Tool Calling", kind="LLM")
async def experiment_eval_golden_links_appear_tool_calling(
    input, output, expected
) -> tuple | bool:

    if input in output:
        response = True
    else:
        response = False

    return response


@create_evaluator(name="Tool Calling", kind="LLM")
async def experiment_eval_tool_calling(input, output, expected) -> float | bool:
    tool_definitions = await get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

    rails_tool_calling = ["correct", "incorrect"]
    results = []

    for tool_call_details in output.get("tool_call_messages", []):
        tool_call = tool_call_details.get("tool_call", {})
        if tool_call.get("name") in ("public_services_grounded_search", "google_search"):
            response = await experiment_eval(
                input=input,
                output=output,
                prompt=TOOL_CALLING_LLM_JUDGE_PROMPT.replace(
                    "{tool_definitions}", tool_definitions
                ),
                rails=rails_tool_calling,
                tool_call=tool_call,
            )

            label = response.get("label") if isinstance(response, dict) else None
            result = int(label == rails_tool_calling[0]) if label else int(response)
            results.append(result)

    return sum(results) / len(results) if results else False


@create_evaluator(name="Simplificação da Busca", kind="LLM")
async def experiment_eval_search_query_effectiveness(
    input, output, expected
) -> float | bool:
    rails_search_query_effectiveness = ["effective", "innefective"]
    results = []

    if output:
        for tool_call_details in output.get("tool_call_messages", []):
            tool_call = tool_call_details.get("tool_call", {})
            if tool_call.get("name") in ("public_services_grounded_search", "google_search"):
                query = await extrair_query(tool_call.get("arguments", ""))
                response = await experiment_eval(
                    input=input,
                    output=output,
                    prompt=SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
                    rails=rails_search_query_effectiveness,
                    search_tool_query=query,
                )

                label = response.get("label") if isinstance(response, dict) else None
                result = (
                    int(label == rails_search_query_effectiveness[0])
                    if label
                    else int(response)
                )
                results.append(result)

    return sum(results) / len(results) if results else False
