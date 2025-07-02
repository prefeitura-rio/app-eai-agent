import asyncio
import re
from typing import List, Union
import httpx
import pandas as pd
import json
from src.evaluations.letta.agents.final_response import (
    ANSWER_COMPLETENESS_LLM_JUDGE_PROMPT,
    CLARITY_LLM_JUDGE_PROMPT,
    EMERGENCY_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ENTITY_PRESENCE_LLM_JUDGE_PROMPT,
    FEEDBACK_HANDLING_COMPLIANCE_JUDGE_PROMPT,
    ANSWER_SIMILARITY_PROMPT,
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

from src.evaluations.letta.phoenix.training_dataset.utils import (
    empty_agent_core_memory,
    experiment_eval,
    final_response,
    tool_returns,
)

from src.evaluations.letta.phoenix.utils import extrair_query, get_system_prompt

from phoenix.experiments.evaluators import create_evaluator
import ast
from urllib.parse import urlparse, unquote
from urllib.parse import urlparse, parse_qsl, urlencode


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


@create_evaluator(name="Tool Calling", kind="LLM")
async def experiment_eval_tool_calling(input, output, expected) -> float | bool:
    tool_definitions = await get_system_prompt()
    tool_definitions = tool_definitions[tool_definitions.find("Available tools:\n") :]

    rails_tool_calling = ["correct", "incorrect"]
    results = []

    for tool_call_details in output.get("tool_call_messages", []):
        tool_call = tool_call_details.get("tool_call", {})
        if tool_call.get("name") in (
            "public_services_grounded_search",
            "google_search",
        ):
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
            if tool_call.get("name") in (
                "public_services_grounded_search",
                "google_search",
            ):
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


@create_evaluator(name="Activate Search Tools")
async def activate_search(output) -> bool | tuple:
    if not output:
        return (False, "No output provided")

    grouped = output.get("agent_output", {}).get("grouped", {})
    tool_msgs = grouped.get("tool_return_messages", [])

    SEARCH_TOOL_NAMES = [
        "public_services_grounded_search",
        "google_search",
        "typesense_search",
        "gpt_search",
    ]

    activated_tools = {
        msg.get("name") for msg in tool_msgs if msg.get("name") in SEARCH_TOOL_NAMES
    }

    explanation = f"Activated tools: {list(activated_tools)}"

    return len(activated_tools) > 0, explanation


def get_answer_links(output):
    grouped = output.get("agent_output", {}).get("grouped", {})
    tool_msgs = grouped.get("tool_return_messages", [])
    answer_links = []
    for msg in tool_msgs:
        tool_return = msg.get("tool_return")
        if tool_return:
            tool_return = json.loads(tool_return)
        else:
            tool_return = {}
        answer_links.extend(tool_return.get("sources", []))

    answer_links_unique = []
    answer_links_set = set()
    for link in answer_links:
        if link.get("url") not in answer_links_set:
            answer_links_set.add(link.get("url"))
            answer_links_unique.append(link)

    return [
        {"label": link.get("label"), "uri": link.get("uri"), "url": link.get("url")}
        for link in answer_links_unique
    ]


@create_evaluator(name="Golden Link in Tool Calling")
async def golden_link_in_tool_calling(output) -> bool | tuple:
    """
    Returns True if the agent output ultimately resolves to at least one of the
    golden links listed in metadata["golden_links_list"].

    Now supports Letta (Vertex), Gemini, and GPT outputs.

    Matching rules
    - Scheme (http/https) is ignored.
    - 'www.' prefix is ignored.
    - Trailing slashes are ignored.
    - If the golden link has a path, the path must match exactly.
    - If the golden link is only a domain, any path on that domain passes.
    """

    if not output:
        return (False, "No output provided")

    golden_field = output.get("metadata", {}).get("golden_links_list", "")

    try:
        golden_links = (
            ast.literal_eval(golden_field)
            if isinstance(golden_field, str)
            else golden_field
        )
    except (ValueError, SyntaxError):
        golden_links = []

    # golden_field = output.get("metadata", {}).get("Golden links", "")
    # golden_links = _parse_golden(golden_field)
    answer_links = get_answer_links(output=output)

    if not answer_links or not golden_links:
        return (False, "No links found in the answer or no golden links provided")

    answer_links, overall_count = match_golden_link(
        answer_links=answer_links, golden_links=golden_links
    )

    match_found = True if overall_count > 0 else False
    explanation = {
        "golden_links": golden_links,
        "answer_links": answer_links,
        "number_of_matches": overall_count,
    }
    return match_found, explanation


# -----------------------------------------------------
# Helper functions – keep them private to avoid namespace pollution
# ---------------------------------------------------------------------------
def match_golden_link(answer_links, golden_links):
    """
    Match golden links in explanation links.
    """
    overall_count = 0
    for answer_link in answer_links:
        url = _norm_url(answer_link.get("url"))
        url = None if url == "" else url
        answer_link["url"] = url

        count = 0
        golden_found = None
        for golden_link in golden_links:
            if str(url) in _norm_url(golden_link):
                answer_link["has_golden_link"] = True
                count += 1
                overall_count += 1
                golden_found = _norm_url(golden_link)

        answer_link["golden_link"] = golden_found
        answer_link["has_golden_link"] = True if count > 0 else False

    answer_links = [
        {
            "has_golden_link": item.get("has_golden_link"),
            "golden_link": item.get("golden_link"),
            "url": item.get("url"),
            "uri": item.get("uri"),
        }
        for item in answer_links
    ]
    reordered_data = sorted(answer_links, key=lambda item: item["golden_link"] is None)

    return reordered_data, overall_count


def _norm_url(url: str) -> str:
    """Lower-case, drop scheme, drop www., strip trailing slash and `:~:text=` fragments."""

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "http://" + url  # makes urlparse happy

    parsed = urlparse(url)

    domain = parsed.netloc.lower().removeprefix("www.")
    path = unquote(parsed.path).lower().rstrip("/")

    if ":~:text=" in path:  # Strip scroll-to-text fragments
        path = path.split(":~:text=")[0]

    # Mantém apenas os parâmetros que NÃO começam com 'utm_source'
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    if query_params and query_params[-1][0] == "utm_source":
        query_params = query_params[:-1]

    query_string = urlencode(query_params)

    norm_url = f"{domain}{path}"
    if query_string:
        norm_url += f"?{query_string}"

    return norm_url


@create_evaluator(name="Golden Link in Answer")
async def golden_link_in_answer(output) -> bool | tuple:
    if not output:
        return (False, "No output provided")

    # golden_field = output.get("metadata", {}).get("Golden links", "")
    # golden_links = _parse_golden(golden_field)

    golden_field = output.get("metadata", {}).get("golden_links_list", "")

    try:
        golden_links = (
            ast.literal_eval(golden_field)
            if isinstance(golden_field, str)
            else golden_field
        )
    except (ValueError, SyntaxError):
        golden_links = []

    resposta = output.get("agent_output", {}).get("texto") or final_response(
        output["agent_output"]
    ).get("content", "")

    markdown_links = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", resposta)
    plain_links = re.findall(r"https?://[^\s)\]]+", resposta)
    raw_links = list(dict.fromkeys(markdown_links + plain_links))

    if not raw_links or not golden_links:
        return (False, "No links found in the answer or no golden links provided")

    normalized_links = [
        f"https://{link}" if not link.startswith("http") else link for link in raw_links
    ]
    unique_links = list(
        dict.fromkeys([link for link in normalized_links if isinstance(link, str)])
    )

    link_dicts = [{"url": url} for url in unique_links]

    answer_links_tool_calling = get_answer_links(output=output)

    answer_links_tool_calling_map = {
        link.get("url"): link.get("uri") for link in answer_links_tool_calling
    }

    answer_links = [
        {
            "url": l.get("url"),
            "uri": answer_links_tool_calling_map.get(l.get("url")),
        }
        for l in link_dicts
    ]

    answer_links, overall_count = match_golden_link(
        answer_links=answer_links, golden_links=golden_links
    )

    match_found = True if overall_count > 0 else False

    explanation = {
        "golden_links": golden_links,
        "answer_links": answer_links,
        "number_of_matches": overall_count,
    }

    return match_found, explanation


@create_evaluator(name="Answer Similarity", kind="LLM")
async def answer_similarity(input, output, expected) -> tuple:
    rails = ["equivalent", "similar", "different"]
    mapping = {"equivalent": 1, "similar": 0.5, "different": 0}

    response = await experiment_eval(
        input=input,
        output=output,
        prompt=ANSWER_SIMILARITY_PROMPT,
        rails=rails,
        expected=expected,
    )

    label = response.iloc[0]["label"]
    explanation = response.iloc[0]["explanation"]

    if label in mapping:
        eval_result = mapping[label]
    else:
        eval_result = 0
        explanation = "Label not recognized or not in mapping"

    return (eval_result, explanation)
