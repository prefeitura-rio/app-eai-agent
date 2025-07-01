import asyncio
import re
from typing import List, Union
import httpx
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

from src.evaluations.letta.phoenix.training_dataset.utils import (
    empty_agent_core_memory,
    experiment_eval,
    final_response,
    get_redirect_links,
    process_link,
    tool_returns,
)

from src.evaluations.letta.phoenix.utils import extrair_query, get_system_prompt

from phoenix.experiments.evaluators import create_evaluator
import ast
from urllib.parse import urlparse, unquote
import json


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
async def experiment_eval_activate_search(output) -> bool | tuple:
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

    activated_tools = []
    for msg in tool_msgs:
        tool_name = msg.get("name")
        if tool_name and tool_name in SEARCH_TOOL_NAMES:
            activated_tools.append(tool_name)

    activated_tools = list(set(activated_tools))
    explanation = f"Activated tools: {activated_tools}"

    return len(activated_tools) > 0, explanation


@create_evaluator(name="Golden Link in Tool Calling")
async def experiment_eval_golden_link_in_tool_calling(output) -> bool | tuple:
    """
    Returns True if the agent output ultimately resolves to at least one of the
    golden links listed in metadata["Golden links"].

    Now supports Letta (Vertex), Gemini, and GPT outputs.

    Matching rules
    - Scheme (http/https) is ignored.
    - 'www.' prefix is ignored.
    - Trailing slashes are ignored.
    - If the golden link has a path, the path must match exactly.
    - If the golden link is only a domain, any path on that domain passes.
    """

    # Sanity checks
    if not output:
        return (False, "No output provided")

    golden_field = output.get("metadata", {}).get("Golden links list", "")

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

    # Resolve answer links
    answer_links: list[str] = []
    link_dicts = []
    explanation_links = []
    if "links" in output["agent_output"]:
        for link in output["agent_output"]["links"]:
            uri = link.get("uri") or link.get("url")
            link_dicts.append({"uri": uri})

        async with httpx.AsyncClient(
            follow_redirects=True, timeout=2, verify=False
        ) as session:
            await asyncio.gather(*(process_link(session, link) for link in link_dicts))

        final_urls = []
        for link in link_dicts:
            if link.get("url"):
                final_urls.append(link["url"])
                explanation_links.append(
                    {
                        "url": link.get("url"),
                        "uri": link.get("uri"),
                        "error": link.get("error"),
                    }
                )
        answer_links = final_urls
    else:
        letta_links, explanation_links = await get_redirect_links(
            output
        )  # provided helper
        answer_links.extend(letta_links)

    if not answer_links or not golden_links:
        return (False, "No links found in the answer or no golden links provided")

    # Normalize for fair compare
    gold_norm = [_norm_url(u) for u in golden_links]
    links_norm = {_norm_url(u) for u in answer_links}

    # Exact-enough comparison (see docstring for the rules)
    def match(gold: str, link: str) -> bool:
        g_dom, g_path = gold.split("/", 1) if "/" in gold else (gold, "")
        l_dom, l_path = link.split("/", 1) if "/" in link else (link, "")

        return g_dom == l_dom and (not g_path or g_path == l_path)

    response = any(match(g, l) for g in gold_norm for l in links_norm)

    explanation = f"Golden links: {golden_links}\nAnswer links: {explanation_links}\nMatch found: {response}"
    return response, explanation


# -----------------------------------------------------
# Helper functions – keep them private to avoid namespace pollution
# ---------------------------------------------------------------------------


def _parse_golden(raw) -> list[str]:
    """Turn metadata['Golden links'] into a clean list."""
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if "http" in str(x)]
    if isinstance(raw, str):
        raw = raw.strip()
        # Try to read a Python-style list first
        try:
            import ast

            parsed = ast.literal_eval(raw)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if "http" in str(x)]
        except Exception:
            pass
        # Fallback: split on comma or whitespace
        sep = "," if "," in raw else None
        return [s.strip() for s in raw.split(sep) if "http" in s]
    return []


def _norm_url(url: str) -> str:
    """Lower-case, drop scheme, drop www., strip trailing slash and `:~:text=` fragments."""
    from urllib.parse import urlparse, unquote

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "http://" + url  # makes urlparse happy

    parsed = urlparse(url)
    domain = parsed.netloc.lower().lstrip("www.")
    path = unquote(parsed.path).rstrip("/").lower()

    if ":~:text=" in path:  # Strip scroll-to-text fragments
        path = path.split(":~:text=")[0]

    return f"{domain}{path}"


@create_evaluator(name="Golden Link in Answer")
async def experiment_eval_golden_link_in_answer(output) -> bool | tuple:
    if not output:
        return (False, "No output provided")

    # golden_field = output.get("metadata", {}).get("Golden links", "")
    # golden_links = _parse_golden(golden_field)

    golden_field = output.get("metadata", {}).get("Golden links list", "")

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

    # pattern = r"(https?://)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,10}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
    # pattern = r"\b(?:https?://|www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}(?:/[^\s]*)?"

    markdown_links = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", resposta)
    plain_links = re.findall(r"https?://[^\s)\]]+", resposta)
    raw_links = list(dict.fromkeys(markdown_links + plain_links))

    if not raw_links or not golden_links:
        return (False, "No links found in the answer or no golden links provided")

    normalized_input_links = [
        f"https://{link}" if not link.startswith("http") else link for link in raw_links
    ]
    unique_links = list(
        dict.fromkeys(
            [link for link in normalized_input_links if isinstance(link, str)]
        )
    )[:10]

    link_dicts = [{"uri": uri} for uri in unique_links]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=5, verify=False, headers=headers
    ) as session:
        await asyncio.gather(*(process_link(session, link) for link in link_dicts))

    explanation_links = [
        {"url": link.get("url"), "uri": link.get("uri"), "error": link.get("error")}
        for link in link_dicts
    ]
    answer_links = [link.get("url") or link.get("uri") for link in link_dicts]

    gold_norm = [_norm_url(u) for u in golden_links]
    links_norm = {_norm_url(u) for u in answer_links}

    def match(gold: str, link: str) -> bool:
        g_dom, g_path = gold.split("/", 1) if "/" in gold else (gold, "")
        l_dom, l_path = link.split("/", 1) if "/" in link else (link, "")

        return g_dom == l_dom and (not g_path or g_path == l_path)

    response = any(match(g, l) for g in gold_norm for l in links_norm)

    explanation = f"Golden links: {golden_links}\nAnswer links: {explanation_links}\nMatch found: {response}"

    return response, explanation
