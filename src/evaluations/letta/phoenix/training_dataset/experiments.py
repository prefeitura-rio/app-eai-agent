import sys
import os
import time
import asyncio
import uuid
from typing import Dict, List, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from src.config import env
from src.evaluations.letta.phoenix.training_dataset.evaluators import *
from src.evaluations.letta.phoenix.llm_models.genai_model import GenAIModel
from src.services.letta.agents.memory_blocks.agentic_search_mb import get_agentic_search_memory_blocks
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

## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: MANDEI A IA COMENTAR O CÓDIGO PARA QUALQUER UM ENTENDA O QUE ESTÁ ACONTECENDO AQUI.
## NOTE: ----------------------------------------------------------------------------------
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.
## NOTE: PARA RODAR O CÓDIGO, TEM UMA PECULIARIDADE EM QUE É PRECISO ALTERAR UM ITEM DA CRIAÇÃO DO AGENTE, QUALQUER DÚVIDA ME CHAMA (FRED) QUE EU EXPLICO O QUE FAZER.

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)

GEMINI_COMPLETO = GeminiService()

# Modelo para avaliação
EVAL_MODEL = OpenAIModel(api_key=env.OPENAI_API_KEY, azure_endpoint=env.OPENAI_URL, api_version="2024-02-15-preview", model="gpt-4.1")

# Tamanho do batch para criação de agentes
BATCH_SIZE = 10

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
            agent_type="agentic_search",
            tags=[f"test_evaluation_{index}"],
            name=name
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

async def obter_resposta_letta(agent_id: str, pergunta: str, nome_usuario: str = "Usuário Teste") -> dict:
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
        resposta = await letta_service.send_message(
            agent_id=agent_id,
            message_content=pergunta,
            name=nome_usuario
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
    logger.info(f"Criando {len(exemplos)} agentes para o batch começando em {inicio_batch}")
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
        pergunta = exemplo.input.get("pergunta")
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
    
    logger.info(f"Iniciando coleta de respostas para {total_exemplos} exemplos em batches de {BATCH_SIZE}")
    
    for i in range(0, total_exemplos, BATCH_SIZE):
        # Determinar o tamanho do batch atual (pode ser menor no final)
        batch_atual = exemplos[i:min(i + BATCH_SIZE, total_exemplos)]
        logger.info(f"Processando batch {i//BATCH_SIZE + 1} com {len(batch_atual)} exemplos")
        
        # Processar o batch
        resultados_batch = await processar_batch(batch_atual, i)
        todas_respostas.update(resultados_batch)
        
        # Log do progresso
        logger.info(f"Progresso: {min(i + BATCH_SIZE, total_exemplos)}/{total_exemplos} exemplos processados")
    
    logger.info(f"Coleta concluída: {len(todas_respostas)}/{total_exemplos} respostas obtidas")
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
            "title": msg.get('tool_return', {}).get('title', ''),
            "summary": msg.get('tool_return', {}).get('summary', '')
        }
        for msg in agent_stream.get("tool_return_messages", [])
        if msg.get('name') == 'search_tool'
    ]

    return search_tool_returns

def empty_agent_core_memory():
    core_memory = [f"{mb['label']}: {mb['value']}" for mb in get_agentic_search_memory_blocks()]

    return "\n".join(core_memory)

async def experiment_eval(input, output, prompt, rails, expected=None, **kwargs) -> tuple| bool:
    if not output:
        return False
    
    df = pd.DataFrame({
        "query": [input.get("pergunta")], 
        "model_response": [final_response(output).get("content", "")], # Letta
    })
    
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

    label = response.get('label')
    if hasattr(label, 'iloc'):
        label = label.iloc[0]
        eval_result = bool(label == rails[0])
    else:
        eval_result = bool(label == rails[0])
    
    explanation = response.get('explanation')
    if hasattr(explanation, 'iloc'):
        explanation = str(explanation.iloc[0])
    else:
        explanation = str(explanation)

    print(f"Query: {input.get('pergunta')}")
    print(f"Label: {label}")
    print(f"Explanation: {explanation}")
    print("---"*20)

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
        return respostas_coletadas.get(example.id, {})
    
    # Executar o experimento Phoenix usando as respostas em cache
    experiment = run_experiment(
        dataset,
        get_cached_responses,
        evaluators=[
            experiment_eval_answer_completeness,
            experiment_eval_groundedness,
            experiment_eval_whatsapp_formatting_compliance,
            experiment_eval_search_result_coverage,
            experiment_eval_good_response_standards,
        ],
        ##TODO: ALTERAR O NOME DO EXPERIMENTO
        experiment_name="Letta - GPT 4.1 Avaliando (Refatorado)", 
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
    dataset_name = "teste_100_exemplos"
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
    