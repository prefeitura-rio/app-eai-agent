import sys
import os
import asyncio

import json


sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import httpx
import pandas as pd
from typing import Dict, List, Any, Literal

from src.services.llm.openai_service import openai_service
from src.services.llm.gemini_service import gemini_service
from phoenix.evals import llm_classify
from phoenix.evals.models import OpenAIModel
from phoenix.experiments.types import Example

from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from src.services.letta.letta_service import letta_service
from src.services.letta.agents.memory_blocks.agentic_search_mb import (
    get_agentic_search_memory_blocks,
)
import logging


# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from src.config import env

if env.EVAL_MODEL_TYPE == "gpt":
    EVAL_MODEL = OpenAIModel(
        api_key=env.OPENAI_AZURE_API_KEY,
        azure_endpoint=env.OPENAI_URL,
        api_version="2025-01-01-preview",
        model=env.GPT_EVAL_MODEL,
    )
else:
    EVAL_MODEL = GenAIModel(
        model=env.GEMINI_EVAL_MODEL, api_key=env.GEMINI_API_KEY, max_tokens=100000
    )


async def get_response_from_gpt(example: Example) -> dict:
    query = f"Moro no Rio de Janeiro. {example.input.get("mensagem_whatsapp_simulada")}"

    response = await openai_service.generate_content(
        query,
        use_web_search=True,
    )

    def remover_utm(url: str) -> str:
        """Remove todos os parâmetros utm_ da URL."""
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        # Mantém apenas os parâmetros que NÃO começam com 'utm_source'
        nova_query = {k: v for k, v in query.items() if not k.startswith("utm_source")}
        return urlunparse(parsed._replace(query=urlencode(nova_query, doseq=True)))

    for link in response.get("links", []):
        if "uri" in link:
            link["uri"] = remover_utm(link["uri"])
    return response


async def get_response_from_gemini(example: Example) -> str:
    query = f"Moro no Rio de Janeiro. {example.input.get("mensagem_whatsapp_simulada")}"

    response = await gemini_service.generate_content(
        query,
        model="gemini-2.5-flash-preview-05-20",
        use_google_search=True,
        response_format="text_and_links",
    )

    return response


async def criar_agente_letta(
    index: int,
    name: str = "Agente Teste",
    tools: list = None,
    model_name: str = None,
    system_prompt: str = None,
    temperature: float = 0.7,
) -> str:
    """
    Cria um agente Letta para avaliação.

    Args:
        index: Índice para identificação do agente
        name: Nome do agente
        tools: Tools do agente
        model_name: Modelo do agente
    Returns:
        str: ID do agente criado
    """
    try:
        agent_id = await letta_service.create_agent(
            name=name,
            agent_type="agentic_search",
            tags=[f"test_evaluation_{index}"],
            tools=tools,
            model_name=model_name,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        # logger.info(f"Agente criado: {agent_id} (índice {index})")
        logger.info(f"Agente criado: {index}")

        return agent_id.id
    except Exception as e:
        logger.error(f"Erro ao criar agente {index}: {str(e)}")
        raise


async def excluir_agente_letta(agent_id: str) -> bool:
    """
    Exclui um agente Letta após o uso.

    Args:
        agent_id: ID do agente a ser excluído

    Returns:
        bool: True se a exclusão for bem-sucedida
    """
    try:
        await letta_service.delete_agent(agent_id)
        logger.info(f"Agente excluído com sucesso: {agent_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao excluir agente {agent_id}: {str(e)}")
        return False


async def obter_resposta_letta(
    agent_id: str, pergunta: str, nome_usuario: str = "Usuário Teste"
) -> dict:
    """
    Obtém uma resposta do agente Letta.

    Args:
        agent_id: ID do agente
        pergunta: Pergunta a ser enviada
        nome_usuario: Nome do usuário

    Returns:
        dict: Resposta do agente em formato bruto
    """
    try:
        query = f"Moro no Rio de Janeiro. {pergunta}"
        resposta = await letta_service.send_message_raw(
            agent_id=agent_id, message_content=query, name=nome_usuario
        )
        return resposta
    except Exception as e:
        logger.error(f"Erro ao obter resposta do agente {agent_id}: {str(e)}")
        return {}


async def processar_batch(
    exemplos: List[Example],
    inicio_batch: int,
    modo: Literal["letta", "gpt", "gemini"] = "letta",
    tools: list = None,
    model_name: str = None,
    system_prompt: str = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Processa um batch de exemplos usando o modo selecionado:
    - 'letta': cria agentes Letta, obtém respostas e exclui os agentes
    - 'gpt': usa o modelo GPT para obter respostas
    - 'gemini': usa o modelo Gemini para obter respostas

    Args:
        exemplos: Lista de exemplos
        inicio_batch: Índice inicial para identificação
        modo: Modo de operação ('letta', 'gpt', 'gemini')

    Returns:
        Dict[str, Any]: Dicionário com as respostas obtidas
    """
    resultados = {}

    if modo == "letta":
        agentes_criados = {}

        # Fase 1: Criar todos os agentes do batch
        logger.info(
            f"Criando {len(exemplos)} agentes para o batch começando em {inicio_batch}"
        )
        criacao_tarefas = []

        for i, exemplo in enumerate(exemplos):
            indice = inicio_batch + i
            criacao_tarefas.append(
                criar_agente_letta(
                    index=indice,
                    tools=tools,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
            )

        ids_agentes = await asyncio.gather(*criacao_tarefas, return_exceptions=True)

        # Verificar quais agentes foram criados com sucesso
        agentes_validos = []
        for i, resultado in enumerate(ids_agentes):
            if isinstance(resultado, Exception):
                logger.error(f"Falha ao criar agente {inicio_batch + i}: {resultado}")
            else:
                agentes_validos.append((exemplos[i], resultado))
                agentes_criados[resultado] = exemplos[i].id

        # Fase 2: Obter respostas dos agentes criados com sucesso
        logger.info(f"Obtendo respostas de {len(agentes_validos)} agentes válidos")
        tarefas_respostas = []

        for exemplo, agent_id in agentes_validos:
            # Recupera a pergunta presente no input do exemplo.
            pergunta = (
                exemplo.input.get("pergunta")
                or exemplo.input.get("pergunta_individual")
                or exemplo.input.get("mensagem_whatsapp_simulada")
                or next(iter(exemplo.input.values()), "")
            )
            if not isinstance(pergunta, str):
                pergunta = str(pergunta)
            tarefas_respostas.append(obter_resposta_letta(agent_id, pergunta))

        respostas = await asyncio.gather(*tarefas_respostas, return_exceptions=True)

        # Processar respostas
        for i, resposta in enumerate(respostas):
            exemplo, agent_id = agentes_validos[i]
            if isinstance(resposta, Exception):
                logger.error(f"Erro ao obter resposta do agente {agent_id}: {resposta}")
            else:
                resultados[exemplo.id] = resposta

        # Fase 3: Excluir todos os agentes
        logger.info(f"Excluindo {len(agentes_criados)} agentes")
        tarefas_exclusao = [
            excluir_agente_letta(agent_id) for agent_id in agentes_criados
        ]
        await asyncio.gather(*tarefas_exclusao, return_exceptions=True)

    elif modo == "gpt":
        logger.info(f"Obtendo respostas GPT para batch {inicio_batch}")
        tarefas_respostas = []

        for exemplo in exemplos:
            tarefas_respostas.append(get_response_from_gpt(exemplo))
        respostas = await asyncio.gather(*tarefas_respostas, return_exceptions=True)

        for i, resposta in enumerate(respostas):
            exemplo = exemplos[i]
            if isinstance(resposta, Exception):
                logger.error(
                    f"Erro ao obter resposta GPT para exemplo {exemplo.id}: {resposta}"
                )
            else:
                resultados[exemplo.id] = resposta

    elif modo == "gemini":
        logger.info(f"Obtendo respostas Gemini para batch {inicio_batch}")
        tarefas_respostas = []

        for exemplo in exemplos:
            tarefas_respostas.append(get_response_from_gemini(exemplo))

        respostas = await asyncio.gather(*tarefas_respostas, return_exceptions=True)

        for i, resposta in enumerate(respostas):
            exemplo = exemplos[i]
            if isinstance(resposta, Exception):
                logger.error(
                    f"Erro ao obter resposta Gemini para exemplo {exemplo.id}: {resposta}"
                )
            else:
                resultados[exemplo.id] = resposta

    else:
        raise ValueError(f"Modo desconhecido: {modo}")

    return resultados


async def coletar_todas_respostas(
    dataset,
    tools: list = None,
    model_name: str = None,
    batch_size: int = None,
    system_prompt: str = None,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """
    Coleta respostas para todo o dataset em batches.

    Args:
        dataset: Dataset do Phoenix

    Returns:
        Dict[str, Any]: Dicionário com todas as respostas
    """
    if batch_size is None:
        batch_size = 10

    exemplos = list(dataset.examples.values())
    total_exemplos = len(exemplos)
    todas_respostas = {}

    logger.info(
        f"Iniciando coleta de respostas para {total_exemplos} exemplos em batches de {batch_size}"
    )

    for i in range(0, total_exemplos, batch_size):
        # Determinar o tamanho do batch atual (pode ser menor no final)
        batch_atual = exemplos[i : min(i + batch_size, total_exemplos)]
        logger.info(
            f"Processando batch {i//batch_size + 1} com {len(batch_atual)} exemplos"
        )

        # Processar o batch
        resultados_batch = await processar_batch(
            exemplos=batch_atual,
            inicio_batch=i,
            modo="letta",
            tools=tools,
            model_name=model_name,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        todas_respostas.update(resultados_batch)

        # Log do progresso
        logger.info(
            f"Progresso: {min(i + batch_size, total_exemplos)}/{total_exemplos} exemplos processados"
        )

    logger.info(
        f"Coleta concluída: {len(todas_respostas)}/{total_exemplos} respostas obtidas"
    )
    return todas_respostas


# def final_response(agent_stream: dict) -> dict:
#     if not agent_stream or "assistant_messages" not in agent_stream:
#         return {}

#     return agent_stream["assistant_messages"][-1]


def final_response(agent_stream: dict) -> dict:
    try:
        return agent_stream.get("grouped", {}).get("assistant_messages", [])[-1]
    except (IndexError, AttributeError):
        return {}


def tool_returns(agent_stream: dict) -> str:
    if not agent_stream:
        return ""

    returns = [
        f"Tool Return {i + 1}:\n"
        f"Tool Name: {msg.get('name', 'Unknown')}\n"
        f"Tool Result: {msg.get('tool_return', '').strip()}\n"
        for i, msg in enumerate(agent_stream.get("tool_return_messages", []))
    ]

    return "\n".join(returns)


def search_tool_returns_summary(agent_stream: dict) -> list[dict]:
    if not agent_stream:
        return []

    search_tool_returns = [
        {
            "title": msg.get("tool_return", {}).get("title", ""),
            "summary": msg.get("tool_return", {}).get("summary", ""),
        }
        for msg in agent_stream.get("tool_return_messages", [])
        if msg.get("name") == "search_tool"
    ]

    return search_tool_returns


def empty_agent_core_memory():
    core_memory = [
        f"{mb['label']}: {mb['value']}" for mb in get_agentic_search_memory_blocks()
    ]

    return "\n".join(core_memory)


async def resolve_redirect_url(url: str) -> str:
    """
    Resolve um link do Vertex para seu destino real.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.head(url)
            return str(response.url)
    except Exception as e:
        return ""


async def process_link(session, link: dict):
    uri = link.get("uri")
    try:
        response = await session.head(uri, follow_redirects=True)
        response.raise_for_status()
        link["url"] = str(response.url)
        link["error"] = None
        return link
    except Exception as e:
        try:
            response = await session.get(uri, follow_redirects=True)
            response.raise_for_status()
            link["url"] = str(response.url)
            link["error"] = None
            return link

        except Exception as e2:
            link["url"] = None
            link["error"] = str(e2)
            return link


async def get_redirect_links(model_response):
    grouped = model_response.get("agent_output", {}).get("grouped", {})
    tool_msgs = grouped.get("tool_return_messages", [])

    SEARCH_TOOL_NAMES = {
        "public_services_grounded_search",
        "google_search",
        "typesense_search",
        "gpt_search",
    }

    def _extract_urls(raw_list):
        urls = []
        for item in raw_list:
            if isinstance(item, str):
                urls.append(item)
            elif isinstance(item, dict):
                url = item.get("url") or item.get("uri")
                if isinstance(url, str):
                    urls.append(url)
        return urls

    links_para_processar = []

    for msg in tool_msgs:
        tool_name = msg.get("name")
        if tool_name not in SEARCH_TOOL_NAMES:
            continue

        try:
            tool_return = json.loads(msg.get("tool_return", "{}"))
        except Exception:
            continue

        links = []

        if isinstance(tool_return, dict):
            if "links" in tool_return:
                links = _extract_urls(tool_return["links"])
            elif "result" in tool_return:
                links = [
                    item.get("url") for item in tool_return["result"] if item.get("url")
                ]
        elif isinstance(tool_return, list):
            links = _extract_urls(tool_return)

        links_para_processar.extend(links)

    unique_links = list(dict.fromkeys([link for link in links_para_processar]))[:10]
    link_dicts = [{"uri": uri} for uri in unique_links]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(
        follow_redirects=True, timeout=5, verify=False, headers=headers
    ) as session:
        await asyncio.gather(*(process_link(session, link) for link in link_dicts))

    final_urls = [link.get("url") or link.get("uri") for link in link_dicts]
    final_links = [
        {"url": link.get("url"), "uri": link.get("uri"), "error": link.get("error")}
        for link in link_dicts
    ]

    return final_urls, final_links


async def experiment_eval(
    input, output, prompt, rails, expected=None, **kwargs
) -> tuple | bool:
    if not output or "agent_output" not in output:
        return False

    df = pd.DataFrame(
        {
            "query": [input.get("mensagem_whatsapp_simulada")],
            "model_response": [
                final_response(output["agent_output"]).get("content", "")
            ],
            "ideal_response": [expected.get("golden_answer", "") if expected else ""],
        }
    )

    response = llm_classify(
        data=df,
        template=prompt,
        rails=rails,
        model=EVAL_MODEL,
        provide_explanation=True,
        run_sync=False,
    )

    return response
