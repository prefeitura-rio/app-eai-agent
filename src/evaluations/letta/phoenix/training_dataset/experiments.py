import json
import re
import sys
import os
import time
import asyncio
import uuid
from typing import Dict, List, Any, Optional

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
from src.services.llm.gemini_service import GeminiService

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

GEMINI_COMPLETO = GeminiService()

# Modelo para avaliação
EVAL_MODEL = OpenAIModel(
    api_key=env.OPENAI_API_KEY,
    azure_endpoint=env.OPENAI_URL,
    api_version="2024-02-15-preview",
    model="gpt-4.1",
)

# Tamanho do batch para criação de agentes
BATCH_SIZE = 18

# Cache para armazenar as respostas coletadas
respostas_coletadas = {}


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
            agent_type="agentic_search", tags=[f"test_evaluation_{index}"], name=name
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
        resposta = await letta_service.send_message_raw(
            agent_id=agent_id, message_content=pergunta, name=nome_usuario
        )
        return resposta
    except Exception as e:
        logger.error(f"Erro ao obter resposta do agente {agent_id}: {str(e)}")
        return {}


async def processar_batch(exemplos: List[Example], inicio_batch: int) -> Dict[str, Any]:
    """
    Processa um batch de exemplos criando agentes, obtendo respostas e depois excluindo os agentes.

    Args:
        exemplos: Lista de exemplos do batch
        inicio_batch: Índice inicial do batch para identificação

    Returns:
        Dict[str, Any]: Dicionário com as respostas obtidas
    """
    resultados = {}
    agentes_criados = {}

    # Fase 1: Criar todos os agentes do batch
    logger.info(
        f"Criando {len(exemplos)} agentes para o batch começando em {inicio_batch}"
    )
    criacao_tarefas = []

    for i, exemplo in enumerate(exemplos):
        indice = inicio_batch + i
        tarefa = criar_agente_letta(indice)
        criacao_tarefas.append(tarefa)

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
        tarefa = obter_resposta_letta(agent_id, pergunta)
        tarefas_respostas.append(tarefa)

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
    tarefas_exclusao = []

    for agent_id in agentes_criados:
        tarefa = excluir_agente_letta(agent_id)
        tarefas_exclusao.append(tarefa)

    await asyncio.gather(*tarefas_exclusao, return_exceptions=True)

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
        resultados_batch = await processar_batch(batch_atual, i)
        todas_respostas.update(resultados_batch)

        # Log do progresso
        logger.info(
            f"Progresso: {min(i + BATCH_SIZE, total_exemplos)}/{total_exemplos} exemplos processados"
        )

    logger.info(
        f"Coleta concluída: {len(todas_respostas)}/{total_exemplos} respostas obtidas"
    )
    return todas_respostas


def final_response(agent_stream: dict) -> dict:
    if not agent_stream or "assistant_messages" not in agent_stream:
        return {}

    return agent_stream["assistant_messages"][-1]


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


async def process_link(session, link: dict):
    uri = link.get("uri")
    try:
        # primeiro tenta HEAD
        response = await session.head(uri, follow_redirects=True)
        response.raise_for_status()
        link["url"] = str(response.url)
        link["error"] = None
    except Exception:
        try:
            # fallback GET (alguns endpoints Vertex não aceitam HEAD)
            response = await session.get(uri, follow_redirects=True)
            response.raise_for_status()
            link["url"] = str(response.url)
            link["error"] = None
        except Exception as e:
            if "http" in str(e):
                link["url"] = "http" + str(e).split("'\n")[0].split("http")[-1]
            else:
                link["url"] = None
            link["error"] = str(e)


async def get_redirect_links(model_response):
    # A estrutura esperada é output -> agent_output -> grouped -> tool_return_messages
    grouped = model_response.get("agent_output", {}).get("grouped", {})
    tool_msgs = grouped.get("tool_return_messages", [])

    # Coleciona URIs em uma lista simples de strings
    links_para_processar: list[str] = []

    # Nomes das ferramentas de busca cujos retornos realmente contêm links de interesse.
    SEARCH_TOOL_NAMES = {
        "search_tool",
        "public_services_grounded_search",
        "google_search",
        "typesense_search",
    }

    def _extract_urls(raw_list):
        """Converte listas heterogêneas (str ou dict) em lista de strings de URL."""
        urls = []
        if isinstance(raw_list, list):
            for item in raw_list:
                if isinstance(item, str):
                    urls.append(item)
                elif isinstance(item, dict):
                    url_val = item.get("url") or item.get("uri")
                    if isinstance(url_val, str):
                        urls.append(url_val)
        return urls

    for msg in tool_msgs:
        # Se houver campo "name", usa-o para filtrar; caso contrário, assume que pode conter links.
        tool_name = msg.get("name")
        if tool_name and tool_name not in SEARCH_TOOL_NAMES:
            continue

        # 1) Se já existe um dicionário estruturado em "tool_return", é o caminho mais simples.
        tool_return = msg.get("tool_return")
        if isinstance(tool_return, dict):
            # Pode vir como {"links": [...]} ou {"result": [{"url": ...}, ...]}
            if tool_return.get("links"):
                links_para_processar.extend(_extract_urls(tool_return["links"]))
            elif tool_return.get("result"):
                links_para_processar.extend([
                    item["url"]
                    for item in tool_return["result"]
                    if item.get("url")
                ])
            # Continue para próximo msg, não precisamos examinar stdout.
            continue

        # 1.b) tool_return como lista de urls/dicts
        if isinstance(tool_return, list):
            links_para_processar.extend(_extract_urls(tool_return))
            continue

        # 2) Fallback: tenta extrair JSON a partir de stdout (string ou lista de strings)
        stdout = msg.get("stdout", "")
        # Se for lista, pega cada item; se for string, coloca em lista com um item
        stdout_list = stdout if isinstance(stdout, list) else [stdout]

        for std in stdout_list:
            if not std:
                continue
            try:
                start_index = std.find("{")
                end_index = std.rfind("}") + 1
                if start_index == -1 or end_index == 0:
                    continue  # não há JSON
                data = ast.literal_eval(std[start_index:end_index])
                if data.get("links"):
                    links_para_processar.extend(_extract_urls(data["links"]))
                elif data.get("result"):
                    links_para_processar.extend([
                        item["url"]
                        for item in data["result"]
                        if item.get("url")
                    ])
            except (ValueError, SyntaxError):
                continue  # ignora stdout não-parseável

    # Filtra links permitidos e remove ruído comum
    ALLOWED_PREFIXES = (
        "https://carioca.rio/servicos/",
        "https://www.1746.rio/hc/pt-br/articles/",
        "https://assistenciasocial.prefeitura.rio/",
        "https://prefeitura.rio/",
    )

    EXCLUDE_KEYWORDS = (
        "termo-de-uso",
        "privacidade",
        "faq",
        "politica",
        "termo de uso",
    )

    def allowed(u: str) -> bool:
        if not u:
            return False
        if not any(u.startswith(p) for p in ALLOWED_PREFIXES):
            return False
        lowered = u.lower()
        return not any(k in lowered for k in EXCLUDE_KEYWORDS)

    unique_links = list({uri for uri in links_para_processar if isinstance(uri, str) and allowed(uri)})

    # Limita a análise aos primeiros 10 links para evitar ruído excessivo
    unique_links = unique_links[:10]

    # Converte em dicts para reutilizar process_link
    link_dicts = [{"uri": uri} for uri in unique_links]

    # Resolve redirecionamentos em paralelo
    async with httpx.AsyncClient(follow_redirects=True, timeout=2, verify=False) as session:
        await asyncio.gather(*(process_link(session, link) for link in link_dicts))

    # Retorna somente URLs finais (link["url"]) ou o próprio uri caso não haja redirect
    final_urls = []
    for link in link_dicts:
        if link.get("url"):
            final_urls.append(link["url"])
        elif link.get("uri"):
            final_urls.append(link["uri"])
    return final_urls


async def experiment_eval(
    input, output, prompt, rails, expected=None, **kwargs
) -> tuple | bool:
    if not output or "agent_output" not in output:
        return False

    agent_output = output["agent_output"]
    metadata = output.get("metadata", {})
    golden_link = metadata.get("Golden links", "")

    df = pd.DataFrame(
        {
            "query": [input.get("pergunta")],
            "model_response": [final_response(agent_output).get("content", "")],
            "golden_link": [golden_link],
        }
    )

    if expected:
        df["ideal_response"] = [expected.get("resposta_ideal")]

    for k, val in kwargs.items():
        if isinstance(val, str):
            df[k] = [val]
        elif isinstance(val, list):
            df[k] = [", ".join(val)]
        else:
            df[k] = [val]

    response = llm_classify(
        data=df,
        template=prompt,
        rails=rails,
        model=EVAL_MODEL,
        provide_explanation=True,
        run_sync=False,
    )

    label = response.get("label")
    if hasattr(label, "iloc"):
        label = label.iloc[0]
        eval_result = bool(label == rails[0])
    else:
        eval_result = bool(label == rails[0])

    explanation = response.get("explanation")
    if hasattr(explanation, "iloc"):
        explanation = str(explanation.iloc[0])
    else:
        explanation = str(explanation)

    print(f"Query: {input.get('pergunta')}")
    print(f"Label: {label}")
    print(f"Explanation: {explanation}")
    print("---" * 20)

    return (eval_result, explanation)


async def executar_avaliacao_phoenix(dataset, respostas_coletadas):
    """
    Executa a avaliação Phoenix usando as respostas já coletadas.

    Args:
        dataset: Dataset do Phoenix
        respostas_coletadas: Dicionário com as respostas já coletadas
    """
    logger.info("Iniciando avaliação Phoenix com as respostas coletadas")

    # Criar uma função personalizada para o Phoenix que retorna as respostas já coletadas
    async def get_cached_responses(example: Example) -> dict:
        return {
            "agent_output": respostas_coletadas.get(example.id, {}),
            "metadata": example.metadata,
        }

    # Executar o experimento Phoenix usando as respostas em cache
    experiment = run_experiment(
        dataset,
        get_cached_responses,
        evaluators=[
            # experiment_eval_answer_completeness,
            # experiment_eval_groundedness,
            # experiment_eval_whatsapp_formatting_compliance,
            # experiment_eval_search_result_coverage,
            # experiment_eval_good_response_standards,
            experiment_eval_golden_link_in_tool_calling,
            # experiment_eval_golden_link_in_answer
        ],
        ##TODO: ALTERAR O NOME DO EXPERIMENTO
        experiment_name="Letta - Verificando golden links",
        ## -----------------------------------
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
    dataset_name = "Golden Dataset - Small Sample"
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
