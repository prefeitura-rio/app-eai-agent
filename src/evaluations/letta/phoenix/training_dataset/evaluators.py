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


def eval_binary(prompt, rails, input, output, extra_kwargs=None):
    extra_kwargs = extra_kwargs or {}
    response = experiment_eval(
        input=input,
        output=output,
        prompt=prompt,
        rails=rails,
        **extra_kwargs,
    )

    return response


@create_evaluator(name="Answer Completeness", kind="LLM")
def experiment_eval_answer_completeness(input, output, expected) -> tuple:
    rails_answer_completeness = ["complete", "incomplete"]

    return eval_binary(
        ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails_answer_completeness,
        input,
        output,
    )


@create_evaluator(name="Clarity", kind="LLM")
def experiment_eval_clarity(input, output, expected) -> tuple:
    rails_clarity = ["clear", "unclear"]

    return eval_binary(
        CLARITY_LLM_JUDGE_PROMPT,
        rails_clarity,
        input,
        output,
    )


@create_evaluator(name="Similarity Ideal Response", kind="LLM")
def experiment_eval_gold_standard_similarity(input, output, expected) -> float | bool:
    rails_gold_standard_similarity = ["equivalent", "similar", "different"]
    mapping = {"equivalent": 1, "similar": 0.5, "different": 0}

    response = experiment_eval(
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


@create_evaluator(name="Emergency Handling", kind="LLM")
def experiment_eval_emergency_handling_compliance(input, output, expected) -> tuple:
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]

    return eval_binary(
        EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_emergency_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Entity Presence", kind="LLM")
def experiment_eval_entity_presence(input, output, expected) -> tuple:
    rails_entity_presence = ["entities_present", "entities_missing"]

    return eval_binary(
        ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails_entity_presence,
        input,
        output,
    )


@create_evaluator(name="Feedback Handling", kind="LLM")
def experiment_eval_feedback_handling_compliance(input, output, expected) -> tuple:
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]

    return eval_binary(
        FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails_feedback_handling_compliance,
        input,
        output,
    )


@create_evaluator(name="Location Policy", kind="LLM")
def experiment_eval_location_policy_compliance(input, output, expected) -> tuple:
    rails_location_policy_compliance = ["compliant", "non_compliant"]

    return eval_binary(
        LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails_location_policy_compliance,
        input,
        output,
    )


@create_evaluator(name="Security and Privacy", kind="LLM")
def experiment_eval_security_privacy_compliance(input, output, expected) -> tuple:
    rails_security_privacy_compliance = ["compliant", "non_compliant"]

    return eval_binary(
        SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails_security_privacy_compliance,
        input,
        output,
    )


@create_evaluator(name="Whatsapp Format", kind="LLM")
def experiment_eval_whatsapp_formatting_compliance(input, output, expected) -> tuple:
    rails_whatsapp_formatting_compliance = ["compliant", "non_compliant"]

    return eval_binary(
        WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails_whatsapp_formatting_compliance,
        input,
        output,
    )


@create_evaluator(name="Groundness", kind="LLM")
def experiment_eval_groundedness(input, output, expected) -> tuple:
    rails_groundedness = ["based", "unfounded"]

    return eval_binary(
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
def experiment_eval_search_result_coverage(input, output, expected) -> tuple:
    rails_search_result_coverage = ["covers", "uncovers"]

    return eval_binary(
        SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
        rails_search_result_coverage,
        input,
        output,
        extra_kwargs={
            "search_tool_results": tool_returns(output),
        },
    )


@create_evaluator(name="Tool Calling", kind="LLM")
def experiment_eval_tool_calling(input, output, expected) -> float | bool:
    tool_definitions = get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

    rails_tool_calling = ["correct", "incorrect"]
    results = []

    for tool_call_details in output.get("tool_call_messages", []):
        tool_call = tool_call_details.get("tool_call", {})
        if tool_call.get("name") in ("typesense_search", "google_search"):
            response = experiment_eval(
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


@create_evaluator(name="Search Tool Abstractness", kind="LLM")
def experiment_eval_search_query_effectiveness(input, output, expected) -> float | bool:
    rails_search_query_effectiveness = ["effective", "innefective"]
    results = []

    if output:
        for tool_call_details in output.get("tool_call_messages", []):
            tool_call = tool_call_details.get("tool_call", {})
            if tool_call.get("name") in ("typesense_search", "google_search"):
                query = extrair_query(tool_call.get("arguments", ""))
                response = experiment_eval(
                    input=input,
                    output=output,
                    prompt=SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
                    rails=rails_search_query_effectiveness,
                    search_tool_query=query,
                )

                label = response.get("label") if isinstance(response, dict) else None
                result = int(label == rails_search_query_effectiveness[0]) if label else int(response)
                results.append(result)
    
    return sum(results) / len(results) if results else False
