import re
import httpx
from openinference.instrumentation import suppress_tracing
from phoenix.evals import llm_classify
from phoenix.trace import SpanEvaluations
import phoenix as px

from src.config import env
from llm_models.genai_model import GenAIModel

model = GenAIModel(
    model="gemini-2.5-flash-preview-04-17", 
    api_key=env.GEMINI_API_KEY,
    )

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")


def extrair_valor(raw_text: str, label: str):
    pattern = rf"{label}\(value=(?P<quote>['\"])(.*?)(?P=quote)"
    match = re.search(pattern, raw_text, re.DOTALL)

    if match:
        texto = match.group(2)
        texto = texto.replace("\\n", " ").strip()
        texto = re.sub(" +", " ", texto)
        return texto
    
    return None


def parse_response(response: str):
    tool_call_match = re.search(r"tool_calls=\[(.*?)\] role=", response, re.DOTALL)
    tool_call = tool_call_match.group(1) if tool_call_match else None

    if tool_call and "send_message" in tool_call:
        message = re.search(r"arguments='\{(.*)\}'", tool_call, re.DOTALL).group(1)
        message = re.sub(r'\s*"request_heartbeat":\s*(true|false)\s*,?', "", message).strip()
        message = re.sub(r"^(\\n|\s)+|(\s|\\n)+$", "", message)
        message = re.search(r'"message":\s*"(.+)"', message, re.DOTALL).group(1)
    else:
        message = None

    tool = re.search(r"name='([^']+)'", tool_call).group(1)

    return tool, message

def extrair_content(raw_text: str):
    match = re.search(r"(?:content|text)='(.*?)'", raw_text)
    return match.group(1) if match else None

def extrair_query(raw_text: str):
    match = re.search(r'"query": "(.*?)"', raw_text)
    return match.group(1) if match else None

def get_system_prompt() -> str:
    url = f"{env.AGENTIC_SEARCH_URL}/system-prompt?agent_type=agentic_search"
    headers = {
        "accept": "application/json", 
        "Authorization": f"Bearer {env.AGENTIC_SEARCH_API_TOKEN}",
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("prompt", "")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        raise RuntimeError(f"Erro ao buscar system prompt: {e}")
    
def eval(df, prompt, rails, eval_name):
    with suppress_tracing():
        result = llm_classify(
            data=df,
            template=prompt,
            rails=rails,
            model=model,
            provide_explanation=True,
        )

    result["score"] = result["label"].apply(lambda label: 1 if label == rails[0] else 0)

    phoenix_client.log_evaluations(
        SpanEvaluations(eval_name=eval_name, dataframe=result),
    )