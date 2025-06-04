from src.evaluations.letta.agents.final_response import (
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    CLARITY_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
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


@create_evaluator(name="Answer Completeness", kind="LLM")
def experiment_eval_answer_completeness(input, output, expected) -> bool:
    rails_answer_completeness = ["complete", "incomplete"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
        rails=rails_answer_completeness,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_answer_completeness[0]
    return response


@create_evaluator(name="Clarity", kind="LLM")
def experiment_eval_clarity(input, output, expected) -> bool:
    rails_clarity = ["clear", "unclear"]
    response = experiment_eval(
        input=input, output=output, prompt=CLARITY_LLM_JUDGE_PROMPT, rails=rails_clarity
    )
    if isinstance(response, dict):
        return response.get("label") == rails_clarity[0]
    return response


@create_evaluator(name="Similarity Ideal Response", kind="LLM")
def experiment_eval_gold_standart_similarity(input, output, expected) -> float | bool:
    rails_gold_standart_similarity = ["equivalent", "similar", "different"]
    gold_standart_similarity_mapping = {"equivalent": 1, "similar": 0.5, "different": 0}
    response = experiment_eval(
        input=input,
        output=output,
        prompt=GOLD_STANDART_SIMILARITY_LLM_JUDGE_PROMPT,
        rails=rails_gold_standart_similarity,
        expected=expected,
    )
    if not isinstance(response, bool):
        label = response.get("label")
        if isinstance(label, str) and label in gold_standart_similarity_mapping:
            return gold_standart_similarity_mapping[label]
        return False
    return False


@create_evaluator(name="Emergency Handling", kind="LLM")
def experiment_eval_emergency_handling_compliance(input, output, expected) -> bool:
    rails_emergency_handling_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_emergency_handling_compliance,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_emergency_handling_compliance[0]
    return response


@create_evaluator(name="Entity Presence", kind="LLM")
def experiment_eval_entity_presence(input, output, expected) -> bool:
    rails_entity_presence = ["entities_present", "entities_missing"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
        rails=rails_entity_presence,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_entity_presence[0]
    return response


@create_evaluator(name="Feedback Handling", kind="LLM")
def experiment_eval_feedback_handling_compliance(input, output, expected) -> bool:
    rails_feedback_handling_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_feedback_handling_compliance,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_feedback_handling_compliance[0]
    return response


@create_evaluator(name="Location Policy", kind="LLM")
def experiment_eval_location_policy_compliance(input, output, expected) -> bool:
    rails_location_policy_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=LOCATION_POLICY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_location_policy_compliance,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_location_policy_compliance[0]
    return response


@create_evaluator(name="Security and Privacy", kind="LLM")
def experiment_eval_security_privacy_compliance(input, output, expected) -> bool:
    rails_security_privacy_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=SECURITY_PRIVACY_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_security_privacy_compliance,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_security_privacy_compliance[0]
    return response


@create_evaluator(name="Whatsapp Format", kind="LLM")
def experiment_eval_whatsapp_formatting_compliance(input, output, expected) -> bool:
    rails_whatsapp_formatting_compliance = ["compliant", "non_compliant"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=WHATSAPP_FORMATTING_COMPLIANCE_JUDGE_PROMPT,
        rails=rails_whatsapp_formatting_compliance,
    )
    if isinstance(response, dict):
        return response.get("label") == rails_whatsapp_formatting_compliance[0]
    return response


@create_evaluator(name="Groundness", kind="LLM")
def experiment_eval_groundedness(input, output, expected) -> bool:
    rails_groundedness = ["based", "unfounded"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=GROUNDEDNESS_LLM_JUDGE_PROMPT,
        rails=rails_groundedness,
        core_memory=empty_agent_core_memory(),
        search_tool_results=tool_returns(output),
    )
    if isinstance(response, dict):
        return response.get("label") == rails_groundedness[0]
    return response


@create_evaluator(name="Search Result Coverage", kind="LLM")
def experiment_eval_search_result_coverage(input, output, expected) -> bool:
    rails_search_result_coverage = ["covers", "uncovers"]
    response = experiment_eval(
        input=input,
        output=output,
        prompt=SEARCH_RESULT_COVERAGE_LLM_JUDGE_PROMPT,
        rails=rails_search_result_coverage,
        search_tool_results=tool_returns(output),
    )
    if isinstance(response, dict):
        return response.get("label") == rails_search_result_coverage[0]
    return response


@create_evaluator(name="Tool Calling", kind="LLM")
def experiment_eval_tool_calling(input, output, expected) -> float | bool:
    tool_definitions = get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]
    rails_tool_calling = ["correct", "incorrect"]

    results = []
    for tool_call_details in output["tool_call_messages"]:
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
            if isinstance(response, dict):
                result = int(response.get("label") == rails_tool_calling[0])
            else:
                result = int(response)
            results.append(result)
    if results:
        return sum(results) / len(results)
    return False


@create_evaluator(name="Search Tool Abstractness", kind="LLM")
def experiment_eval_search_query_effectiveness(input, output, expected) -> float | bool:
    rails_search_query_effectiveness = ["effective", "innefective"]

    results = []
    for tool_call_details in output["tool_call_messages"]:
        tool_call = tool_call_details.get("tool_call", {})
        if tool_call.get("name") in ("typesense_search", "google_search"):
            tool_call_arguments = tool_call.get("arguments", "")
            response = experiment_eval(
                input=input,
                output=output,
                prompt=SEARCH_QUERY_EFFECTIVENESS_LLM_JUDGE_PROMPT,
                rails=rails_search_query_effectiveness,
                search_tool_query=extrair_query(tool_call_arguments),
            )
            if isinstance(response, dict):
                result = int(
                    response.get("label") == rails_search_query_effectiveness[0]
                )
            else:
                result = int(response)
            results.append(result)
    if results:
        return sum(results) / len(results)
    return False
