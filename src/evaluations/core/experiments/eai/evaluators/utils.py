import ast
import re
from typing import List, Dict, Any
import json
from urllib.parse import urlparse, unquote, parse_qsl, urlencode
from src.utils.log import logger
from src.services.letta.agents.agentic_search_agent import (
    _get_system_prompt_from_api,
    _update_system_prompt_from_api,
)


async def get_system_prompt_version(system_prompt: str):
    result = await _get_system_prompt_from_api(agent_type="agentic_search")
    current_api_system_prompt_clean = (
        result["prompt"].replace(" ", "").replace("\n", "")
    )
    system_prompt_clean = system_prompt.replace(" ", "").replace("\n", "")
    if current_api_system_prompt_clean == system_prompt_clean:
        logger.info(
            f"Same system prompt detected. Returning version: {result['version']}"
        )
        return result["version"]
    else:
        response = await _update_system_prompt_from_api(
            agent_type="agentic_search", new_system_prompt=system_prompt
        )
        logger.info(
            f"Different system prompt detected. Returning version: {result['version']}"
        )
        return response["version"]


def parse_golden_links(links: str) -> List[str]:
    try:
        return ast.literal_eval(links) if isinstance(links, str) else links
    except Exception:
        return []


def extract_links_from_text(text: str) -> List[str]:
    markdown_links = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", text)
    plain_links = re.findall(r"https?://[^\s)\]]+", text)
    normalized = [
        link if link.startswith("http") else f"https://{link}"
        for link in markdown_links + plain_links
    ]
    return list(dict.fromkeys(normalized))


def match_golden_link(answer_links, golden_links):
    """
    Match golden links in explanation links.
    """
    overall_count = 0
    for answer_link in answer_links:
        url = _norm_url(answer_link)
        count = 0
        golden_found = None
        for golden_link in golden_links:
            if url in _norm_url(golden_link):
                answer_link["golden_link"] = True
                count += 1
                overall_count += 1
                golden_found = _norm_url(golden_link)

        answer_link["golden_link"] = golden_found
        answer_link["golden_link"] = True if count > 0 else False

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
