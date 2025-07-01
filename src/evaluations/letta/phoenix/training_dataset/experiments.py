import json
import re
import sys
import os
import time
import asyncio
import uuid
from typing import Dict, List, Any, Literal
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)

from src.config import env
from src.evaluations.letta.phoenix.training_dataset.evaluators import *
from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
from src.services.letta.agents.memory_blocks.agentic_search_mb import (
    get_agentic_search_memory_blocks,
)
from src.services.letta.letta_service import letta_service

os.environ["PHOENIX_HOST"] = env.PHOENIX_HOST
os.environ["PHOENIX_PORT"] = env.PHOENIX_PORT
os.environ["PHOENIX_ENDPOINT"] = env.PHOENIX_ENDPOINT

import pandas as pd
import httpx
import phoenix as px
import nest_asyncio
from src.services.llm.gemini_service import gemini_service
from src.services.llm.openai_service import openai_service

from phoenix.evals import llm_classify
from phoenix.evals.models import OpenAIModel
from phoenix.experiments.types import Example
from phoenix.experiments import run_experiment
import logging

import urllib3
import ast

## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: ----------------------------------------------------------------------------------
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)


# EVAL_MODEL = GenAIModel(
#     model=env.GEMINI_EVAL_MODEL, api_key=env.GEMINI_API_KEY, max_tokens=100000
# )

EVAL_MODEL = OpenAIModel(
    api_key=env.OPENAI_AZURE_API_KEY,
    azure_endpoint=env.OPENAI_URL,
    api_version="2025-01-01-preview",
    model="gpt-4o",
)

# Tamanho do batch para criação de agentes
BATCH_SIZE = 15

# Cache para armazenar as respostas coletadas
respostas_coletadas = {}


async def get_response_from_gpt(example: Example) -> dict:
    query = f"Moro no Rio de Janeiro. {example.input.get("Mensagem WhatsApp Simulada")}"

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
    query = f"Moro no Rio de Janeiro. {example.input.get("Mensagem WhatsApp Simulada")}"

    response = await gemini_service.generate_content(
        query,
        model="gemini-2.5-flash-preview-05-20",
        use_google_search=True,
        response_format="text_and_links",
    )

    return response


async def criar_agente_letta(index: int, name: str = "Agente Teste") -> str:
    """
    Cria um agente Letta para avaliação.

    Args:
        index: Índice para identificação do agente
        name: Nome do agente

    Returns:
        str: ID do agente criado
    """
    try:
        agent_id = await letta_service.create_agent(
            name=name,
            agent_type="agentic_search",
            tags=[f"test_evaluation_{index}"],
        )
        logger.info(f"Agente criado: {agent_id} (índice {index})")
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
            criacao_tarefas.append(criar_agente_letta(indice))

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
                or exemplo.input.get("Mensagem WhatsApp Simulada")
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
            # pergunta = (
            #     exemplo.input.get("pergunta")
            #     or exemplo.input.get("pergunta_individual")
            #     or exemplo.input.get("Mensagem WhatsApp Simulada")
            #     or next(iter(exemplo.input.values()), "")
            # )

            # if not isinstance(pergunta, str):
            #     pergunta = str(pergunta)
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
            # pergunta = (
            #     exemplo.input.get("pergunta")
            #     or exemplo.input.get("pergunta_individual")
            #     or exemplo.input.get("Mensagem WhatsApp Simulada")
            #     or next(iter(exemplo.input.values()), "")
            # )

            # if not isinstance(pergunta, str):
            #     pergunta = str(pergunta)
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


async def coletar_todas_respostas(dataset) -> Dict[str, Any]:
    """
    Coleta respostas para todo o dataset em batches.

    Args:
        dataset: Dataset do Phoenix

    Returns:
        Dict[str, Any]: Dicionário com todas as respostas
    """
    exemplos = list(dataset.examples.values())
    total_exemplos = len(exemplos)
    todas_respostas = {}

    logger.info(
        f"Iniciando coleta de respostas para {total_exemplos} exemplos em batches de {BATCH_SIZE}"
    )

    for i in range(0, total_exemplos, BATCH_SIZE):
        # Determinar o tamanho do batch atual (pode ser menor no final)
        batch_atual = exemplos[i : min(i + BATCH_SIZE, total_exemplos)]
        logger.info(
            f"Processando batch {i//BATCH_SIZE + 1} com {len(batch_atual)} exemplos"
        )

        # Processar o batch
        resultados_batch = await processar_batch(batch_atual, i, modo="letta")
        todas_respostas.update(resultados_batch)

        # Log do progresso
        logger.info(
            f"Progresso: {min(i + BATCH_SIZE, total_exemplos)}/{total_exemplos} exemplos processados"
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


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def process_link(session: httpx.AsyncClient, link: dict) -> dict:
    uri = link.get("uri")

    try:
        response = await session.head(uri, follow_redirects=True)
        link["url"] = str(response.url)
        link["error"] = None
    except Exception as e:
        try:
            response = await session.get(uri, follow_redirects=True)
            link["url"] = str(response.url)
            link["error"] = None

        except Exception as e2:
            link["url"] = None
            link["error"] = str(e2)
            return link
        
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
                url_val = item.get("url") or item.get("uri")
                if isinstance(url_val, str):
                    urls.append(url_val)
        return urls

    links_para_processar = []

    for msg in tool_msgs:
        tool_name = msg.get("name")
        if tool_name and tool_name not in SEARCH_TOOL_NAMES:
            continue

        try:
            tool_return = json.loads(msg.get("tool_return", "{}"))
        except Exception:
            continue

        links = _extract_urls(tool_return)
        links_para_processar.extend(links)

    unique_links = list(dict.fromkeys([links_para_processar]))[:10]
    link_dicts = [{"uri": uri} for uri in unique_links]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=5, verify=False, headers=headers) as session:
        await asyncio.gather(*(process_link(session, link) for link in link_dicts))

    # Retorna a lista só com URLs finais corrigidos (ou original se não redirecionou)
    final_urls = [link.get("url") or link.get("uri") for link in link_dicts]
    final_info = [
        {"url": link.get("url"), "uri": link.get("uri"), "error": link.get("error")}
        for link in link_dicts
    ]
    
    return final_urls, final_info


async def experiment_eval(
    input, output, prompt, rails, expected=None, **kwargs
) -> tuple | bool:
    if not output or "agent_output" not in output:
        return False

    df = pd.DataFrame({
        "query": [input.get("Mensagem WhatsApp Simulada", "")],
        "model_response": [final_response(output["agent_output"]).get("content", "")],
        "ideal_response": [expected.get("Golden Answer", "") if expected else ""],
    })

    response = llm_classify(
        data=df,
        template=prompt,
        rails=rails,
        model=EVAL_MODEL,
        provide_explanation=True,
        run_sync=False,
        verbose=True
    )

    return response


async def executar_avaliacao_phoenix(dataset, respostas_coletadas):
    """
    Executa a avaliação Phoenix usando as respostas já coletadas.

    Args:
        dataset: Dataset do Phoenix
        respostas_coletadas: Dicionário com as respostas já coletadas
    """
    logger.info("Iniciando avaliação Phoenix com as respostas coletadas")

    async def get_cached_responses(example: Example) -> dict:
        return {
            "agent_output": respostas_coletadas.get(example.id, {}),
            "metadata": example.metadata,
        }

    experiment = run_experiment(
        dataset,
        get_cached_responses,
        evaluators=[
            # experiment_eval_answer_completeness,
            # experiment_eval_groundedness,
            # experiment_eval_whatsapp_formatting_compliance,
            # experiment_eval_search_result_coverage,
            # experiment_eval_good_response_standards,
            golden_link_in_tool_calling,
            golden_link_in_answer,
            activate_search,
            answer_similarity,
        ],
        experiment_name="eai-2025-06-27-v17",
        experiment_description="Evaluating final response of the agent with various evaluators.",
        dry_run=False,
        concurrency=10,
    )

    logger.info("Avaliação Phoenix concluída")
    return experiment


async def main():
    """Função principal que executa todo o processo"""
    logger.info("Iniciando a execução do script...")

    ##TODO: ALTERAR AQUI O DATASET QUE SERÁ AVALIADO

    datasets_names = [
        "golden_dataset_super_small_sample_v2",
        # "golden_dataset_small_sample_v2",
        # "golden_dataset_small_sample_v3",
        # "golden_dataset_v3",
        # "golden_dataset",
        # "golden_dataset_small_sample",
    ]

    dataset_name = datasets_names[0]
    logger.info(f"Carregando dataset: {dataset_name}")
    dataset = phoenix_client.get_dataset(name=dataset_name)

    # Etapa 1: Coletar todas as respostas em batches
    logger.info("Iniciando coleta de respostas em batches")
    respostas = await coletar_todas_respostas(dataset)

    # Etapa 2: Executar avaliação Phoenix
    logger.info("Iniciando avaliação Phoenix")
    await executar_avaliacao_phoenix(dataset, respostas)

    logger.info("Processo completo!")


if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
