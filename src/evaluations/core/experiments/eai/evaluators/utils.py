import ast
import re
from typing import List, Optional
import unicodedata
from urllib.parse import urlparse, unquote, parse_qsl, urlencode


def parse_golden_links(links: str) -> List[str]:
    try:
        return ast.literal_eval(links) if isinstance(links, str) else links
    except Exception:
        return []


def extract_links_from_text(text: Optional[str]) -> List[str]:
    markdown_links = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", text)
    plain_links = re.findall(r"https?://[^\s)\]]+", text)
    normalized = [
        link.strip().strip('.') if link.startswith("http") else f"https://{link}"
        for link in markdown_links + plain_links
    ]
    return list(dict.fromkeys(normalized))


def match_golden_link(answer_links, golden_links):
    """
    Match golden links in explanation links.
    """
    overall_count = 0
    result = []

    for answer_url in answer_links:
        url_norm = _norm_url(answer_url)
        matched_golden = None

        for golden_link in golden_links:
            if url_norm in _norm_url(golden_link):
                matched_golden = golden_link
                overall_count += 1
                break

        result.append(
            {
                "url": answer_url,
                "golden_link": matched_golden,
                "has_golden_link": matched_golden is not None,
            }
        )

    reordered_data = sorted(result, key=lambda item: not item["has_golden_link"])

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

    path = ''.join(
        c for c in unicodedata.normalize('NFD', path)
        if unicodedata.category(c) != 'Mn'
    )

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
