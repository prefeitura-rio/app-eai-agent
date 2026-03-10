from typing import Optional, Tuple

from google import genai

import src.config.env as env


def _normalize_gemini_model(model_name: Optional[str]) -> str:
    raw_model = (model_name or env.LLM_MODEL or "gemini-2.5-flash").strip()
    # Alguns pontos do sistema usam prefixo de provider (ex.: "google_ai/gemini-2.5-flash")
    return raw_model.split("/")[-1]


async def estimate_prompt_tokens(
    prompt: str, model_name: Optional[str] = None
) -> Tuple[int, str]:
    """
    Estima tokens para um prompt.

    Retorna:
        (token_count, tokenizer_name)
    """
    text = prompt or ""
    model = _normalize_gemini_model(model_name)

    try:
        client = genai.Client(api_key=env.GEMINI_API_KEY)
        response = await client.aio.models.count_tokens(
            model=model,
            contents=text,
        )
        return int(response.total_tokens or 0), f"gemini_count_tokens:{model}"
    except Exception:
        # Fallback resiliente para não bloquear salvamento do prompt.
        token_count = max(1, round(len(text) / 4)) if text else 0
        return token_count, "gemini_fallback_chars_div4"
