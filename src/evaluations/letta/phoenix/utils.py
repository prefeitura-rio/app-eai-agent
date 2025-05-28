import re
import httpx
from openinference.instrumentation import suppress_tracing
from phoenix.evals import llm_classify
from src.config import env
from llm_models.genai_model import GenAIModel
from phoenix.trace import SpanEvaluations
import phoenix as px



model = GenAIModel(model="gemini-2.5-flash-preview-04-17", api_key=env.GEMINI_API_KEY)
phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")


def extrair_valor(texto, label):
    match = re.search(
        rf"{label}\(value=(?P<quote>['\"])(.*?)(?P=quote)", texto, re.DOTALL
    )
    if match:
        texto_extraido = match.group(2)
        texto_limpo = texto_extraido.replace("\\n", " ").strip()
        texto_limpo = re.sub(" +", " ", texto_limpo)
        return texto_limpo
    return None


def parse_response(response):
    tool_call = re.search(r"tool_calls=\[(.*?)\]", response)
    tool_call = tool_call.group(1) if tool_call else None

    if tool_call and "send_message" in tool_call:
        message = re.search(r"arguments='\{(.*)\}'", tool_call, re.DOTALL).group(1)
        message = re.sub(
            r'\s*"request_heartbeat":\s*(true|false)\s*,?', "", message
        ).strip()
        message = re.sub(r"^(\\n|\s)+|(\s|\\n)+$", "", message)
        message = re.search(r'"message":\s*"(.+)"', message, re.DOTALL).group(1)
    else:
        message = None

    tool = re.search(r"name='([^']+)'", tool_call).group(1)

    return tool, message

def extrair_content(texto):
    match_simples = re.search(r"content='(.*?)'", texto)
    if match_simples:
        return match_simples.group(1)
    
    match_textcontent = re.search(r"text='(.*?)'", texto)
    if match_textcontent:
        return match_textcontent.group(1)
    
    return None

def extrair_query(texto):
    match = re.search(r'"query": "(.*?)"', texto)
    if match:
        return match.group(1)
    return None

def get_system_prompt() -> str:
    url = env.AGENTIC_SEARCH_URL + "/system-prompt?agent_type=agentic_search"
    bearer_token = env.AGENTIC_SEARCH_API_TOKEN
    headers = {"accept": "application/json", "Authorization": f"Bearer {bearer_token}"}
    response = httpx.get(url, headers=headers)
    return response.json()["prompt"]

def eval(df, prompt, rails, eval_name):
    with suppress_tracing():
        test_eval = llm_classify(
            data=df,
            template=prompt,
            rails=rails,
            model=model,
            provide_explanation=True,
        )

    test_eval["score"] = test_eval.apply(lambda x: 1 if x["label"] == rails[0] else 0, axis=1)

    phoenix_client.log_evaluations(
        SpanEvaluations(eval_name=eval_name, dataframe=test_eval),
    )