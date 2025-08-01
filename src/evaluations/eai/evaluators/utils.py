import ast
import re
from typing import List, Dict, Any


def parse_golden_links(agent_response: Dict[str, Any]) -> List[str]:
    field = agent_response.get("metadata", {}).get("golden_links_list", "")
    try:
        return ast.literal_eval(field) if isinstance(field, str) else field
    except Exception:
        return []


def extract_answer_text(agent_response: Dict[str, Any]) -> str:
    return (
        agent_response.get("agent_output").get("resposta_gpt")
        or agent_response.get("agent_output", {}).get("texto")
        or agent_response.get("grouped", {})
        .get("assistant_messages", [])[-1]
        .get("content", "")
    )


def extract_links_from_text(text: str) -> List[str]:
    markdown_links = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", text)
    plain_links = re.findall(r"https?://[^\s)\]]+", text)
    normalized = [
        link if link.startswith("http") else f"https://{link}"
        for link in markdown_links + plain_links
    ]
    return list(dict.fromkeys(normalized))
