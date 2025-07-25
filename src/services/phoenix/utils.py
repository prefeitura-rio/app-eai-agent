import ast
import httpx
import json
import random

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from loguru import logger

from fastapi import HTTPException, HTTPException


class ExperimentDataProcessor:
    """Processador de dados de experimentos."""

    def __init__(self):
        # Esta classe não precisa de estado inicial, mas manter o __init__ é comum
        # se métodos auxiliares forem adicionados que dependam dela futuramente.
        pass

    def parse_json_strings_recursively(self, obj: Any) -> Any:
        """Converte strings JSON em objetos Python recursivamente."""
        if isinstance(obj, dict):
            return {
                key: self.parse_json_strings_recursively(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self.parse_json_strings_recursively(item) for item in obj]
        elif isinstance(obj, str):
            try:
                cleaned_str = obj.strip()
                # Verifica se a string parece um JSON ou lista JSON
                if cleaned_str.startswith(("{", "[")) and cleaned_str.endswith(
                    ("}", "]")
                ):
                    data = json.loads(obj)
                    return self.parse_json_strings_recursively(data)
                else:
                    return obj  # Não é JSON, retorna a string original
            except json.JSONDecodeError:
                # Se falhar como JSON, tenta como literal Python (ex: tuple, dict, list sem aspas no key)
                try:
                    data = ast.literal_eval(obj)
                    return self.parse_json_strings_recursively(data)
                except (ValueError, SyntaxError, TypeError):
                    return (
                        obj  # Não é JSON nem literal Python, retorna a string original
                    )
            except (TypeError, ValueError):
                return obj  # Outros erros de tipo/valor, retorna a string original
        else:
            return obj  # Não é string, dict ou list, retorna o objeto original

    def process_experiment_output(self, output: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa dados de saída do experimento."""
        processed_output = self.parse_json_strings_recursively(output)

        # Extrair metadados do experimento, assumindo que eles estão no primeiro item
        experiment_metadata = {}
        if processed_output and "experiment_metadata" in processed_output[0].get(
            "output", {}
        ):
            experiment_metadata = processed_output[0]["output"]["experiment_metadata"]

        # Processar cada item
        for item in processed_output:
            item["example_id_clean"] = item["example_id"].replace("==", "")

            # Remover metadados do experimento de cada item após extração global
            if "experiment_metadata" in item.get("output", {}):
                item["output"].pop("experiment_metadata")

            # Transformar resposta_gpt se existir
            if "resposta_gpt" in item.get("output", {}).get("agent_output", {}):
                logger.info("resposta_gpt encontrada - processando")
                agent_output = item["output"]["agent_output"]
                item["output"]["agent_output"] = self._transform_agent_output(
                    agent_output
                )

        return {
            "experiment_metadata": experiment_metadata,
            "experiment": processed_output,
        }

    def _transform_agent_output(self, agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma a estrutura do agent_output para o formato esperado."""
        # Essa transformação é bem específica e pode ser mantida como um método privado
        # para clareza e encapsulamento dentro do processador.
        return {
            "grouped": {
                "assistant_messages": {"content": agent_output["resposta_gpt"]},
            },
            "tool_return_messages": [
                {"tool_return": {"text": "", "sources": agent_output.get("fontes", [])}}
            ],
            "ordered": [
                {
                    "type": "tool_return_message",
                    "message": {
                        "tool_return": {
                            "text": "",
                            "sources": agent_output.get("fontes", []),
                            "message_type": "tool_return_message",
                        }
                    },
                },
                {
                    "type": "assistant_message",
                    "message": {
                        "content": agent_output["resposta_gpt"],
                        "message_type": "assistant_message",
                    },
                },
            ],
        }

    def get_experiment_json_data_clean(
        self,
        processed_data: Dict[str, Any],
        number_of_random_experiments: int = 10,
        filter_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Limpa os dados do experimento para um formato mais limpo e organizado"""
        experiment_metadata = processed_data.get("experiment_metadata", {})
        experiment = processed_data.get("experiment", [])

        # Extrair metadados do experimento, assumindo que eles estão no primeiro item
        clean_experiment = []
        for item in experiment:
            exp = {
                "message_id": item.get("output", {}).get("metadata", {}).get("id"),
                "menssagem": item.get("input", {}).get("mensagem_whatsapp_simulada"),
                "golden_answer": item.get("reference_output", {}).get("golden_answer"),
                "model_response": (
                    item.get("output", {})
                    .get("agent_output", {})
                    .get("grouped", {})
                    .get("assistant_messages", [])[0]
                    .get("content", {})
                    if item.get("output", {})
                    .get("agent_output", {})
                    .get("grouped", {})
                    .get("assistant_messages", [])
                    else None
                ),
                # "golden_links_list": item.get("output", {})
                # .get("metadata", {})
                # .get("golden_links_list"),
            }

            reasoning_messages = (
                item.get("output", {}).get("agent_output", {}).get("ordered", {})
            )

            reasoning_list = []
            for step, message in enumerate(reasoning_messages):

                if message.get("type") in [
                    "reasoning_message",
                    "tool_call_message",
                    "tool_return_message",
                ]:
                    reasoning_data = {}

                    reasoning_data["step"] = step
                    reasoning_data["type"] = message.get("type")

                    if message.get("type") == "reasoning_message":
                        reasoning_data["content"] = message.get("message", {}).get(
                            "reasoning"
                        )

                    elif message.get("type") == "tool_call_message":
                        reasoning_data["content"] = {
                            "name": message.get("message", {})
                            .get("tool_call", {})
                            .get("name"),
                            "query": message.get("message", {})
                            .get("tool_call", {})
                            .get("arguments", {})
                            .get("query"),
                        }
                    elif message.get("type") == "tool_return_message":
                        try:
                            reasoning_data["content"] = {
                                "name": message.get("message", {}).get("name"),
                                "text": message.get("message", {})
                                .get("tool_return", {})
                                .get("text"),
                                "sources": message.get("message", {})
                                .get("tool_return", {})
                                .get("sources"),
                                "web_search_queries": message.get("message", {})
                                .get("tool_return", {})
                                .get("web_search_queries"),
                            }
                        except Exception as e:
                            reasoning_data["content"] = {
                                "name": message.get("message", {}).get("name"),
                                "text": message.get("message", {}).get(
                                    "tool_return", {}
                                ),
                            }
                    reasoning_list.append(reasoning_data)

                exp["reasoning_messages"] = reasoning_list

            # metrics
            annotation_metrics = item.get("annotations", {})
            metrics = []
            for annotation in annotation_metrics:
                metric_data = {
                    "annotation_name": annotation.get("name"),
                    "score": annotation.get("score"),
                    "explanation": annotation.get("explanation"),
                }
                metrics.append(metric_data)

            exp["metrics"] = metrics
            clean_experiment.append(exp)

        experiment_metadata["total_runs"] = len(clean_experiment)

        # Apply filters if provided
        if filter_config:
            clean_experiment = self._apply_filters(clean_experiment, filter_config)

        if number_of_random_experiments:
            runs = len(clean_experiment)
            # generate N random experiment numbers
            random_runs = random.sample(range(runs), number_of_random_experiments)
            clean_experiment = [clean_experiment[i] for i in random_runs]
            experiment_metadata["run_samples"] = number_of_random_experiments
        return {
            "experiment_metadata": experiment_metadata,
            "experiment": clean_experiment,
        }

    def _apply_filters(
        self, experiments: List[Dict[str, Any]], filter_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Aplica filtros aos experimentos conforme configuração.

        Filter config structure:
        {
            "basic_fields": ["message_id", "menssagem", "golden_answer", "model_response"],
            "reasoning_messages": {
                "include": True/False,
                "selected_tools": ["tool1", "tool2"] or None for all
            },
            "tool_call_messages": {
                "include": True/False,
                "selected_tools": ["tool1", "tool2"] or None for all
            },
            "tool_return_messages": {
                "include": True/False,
                "selected_tools": ["tool1", "tool2"] or None for all,
                "selected_content": ["sources", "text", "web_search_queries"] or None for all
            },
            "metrics": {
                "include": True/False,
                "selected_metrics": ["metric1", "metric2"] or None for all
            }
        }
        """
        filtered_experiments = []

        for exp in experiments:
            filtered_exp = {}

            # Filter basic fields
            basic_fields = filter_config.get("basic_fields", [])
            for field in basic_fields:
                if field in exp:
                    filtered_exp[field] = exp[field]

            # Filter reasoning messages
            reasoning_config = filter_config.get("reasoning_messages", {})
            tool_call_config = filter_config.get("tool_call_messages", {})
            tool_return_config = filter_config.get("tool_return_messages", {})

            if (
                reasoning_config.get("include")
                or tool_call_config.get("include")
                or tool_return_config.get("include")
            ):
                filtered_reasoning = self._filter_reasoning_messages(
                    exp.get("reasoning_messages", []),
                    reasoning_config,
                    tool_call_config,
                    tool_return_config,
                )
                if filtered_reasoning:
                    filtered_exp["reasoning_messages"] = filtered_reasoning

            # Filter metrics
            metrics_config = filter_config.get("metrics", {})
            if metrics_config.get("include"):
                filtered_metrics = self._filter_metrics(
                    exp.get("metrics", []), metrics_config
                )
                if filtered_metrics:
                    filtered_exp["metrics"] = filtered_metrics

            # Only add experiment if it has content
            if filtered_exp:
                filtered_experiments.append(filtered_exp)

        return filtered_experiments

    def _filter_reasoning_messages(
        self,
        reasoning_messages: List[Dict[str, Any]],
        reasoning_config: Dict[str, Any],
        tool_call_config: Dict[str, Any],
        tool_return_config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter reasoning messages based on type and tool selection"""
        filtered_messages = []

        for msg in reasoning_messages:
            msg_type = msg.get("type")
            include_message = False
            filtered_msg = {}

            # Include reasoning_message if configured
            if msg_type == "reasoning_message" and reasoning_config.get("include"):
                include_message = True
                filtered_msg = msg.copy()

            # Include tool_call_message if configured
            elif msg_type == "tool_call_message" and tool_call_config.get("include"):
                tool_name = msg.get("content", {}).get("name")
                selected_tools = tool_call_config.get("selected_tools")

                if selected_tools is None or tool_name in selected_tools:
                    include_message = True
                    filtered_msg = msg.copy()

            # Include tool_return_message if configured
            elif msg_type == "tool_return_message" and tool_return_config.get(
                "include"
            ):
                tool_name = msg.get("content", {}).get("name")
                selected_tools = tool_return_config.get("selected_tools")
                selected_content = tool_return_config.get("selected_content")

                if selected_tools is None or tool_name in selected_tools:
                    include_message = True

                    # Filter content if specific content fields are selected
                    if selected_content is not None:
                        filtered_content = {}
                        content = msg.get("content", {})

                        # Always include basic fields
                        if "name" in content:
                            filtered_content["name"] = content["name"]

                        # Include selected content fields
                        for field in selected_content:
                            if field in content:
                                filtered_content[field] = content[field]

                        filtered_msg = msg.copy()
                        filtered_msg["content"] = filtered_content
                    else:
                        filtered_msg = msg.copy()

            if include_message:
                filtered_messages.append(filtered_msg)

        return filtered_messages

    def _filter_metrics(
        self, metrics: List[Dict[str, Any]], metrics_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter metrics based on selection"""
        selected_metrics = metrics_config.get("selected_metrics")

        if selected_metrics is None:
            return metrics  # Return all metrics

        filtered_metrics = []
        for metric in metrics:
            if metric.get("annotation_name") in selected_metrics:
                filtered_metrics.append(metric)

        return filtered_metrics


@dataclass
class PhoenixConfig:
    """Configuração para conexão com o serviço Phoenix"""

    endpoint: str
    timeout: float = 30.0

    @property
    def graphql_url(self) -> str:
        """Retorna a URL do GraphQL endpoint"""
        base = self.endpoint.rstrip("/")
        return f"{base}/graphql"

    def experiment_json_url(self, experiment_id: str) -> str:
        """Retorna a URL para buscar dados JSON de um experimento"""
        base = self.endpoint.rstrip("/")
        return f"{base}/v1/experiments/{experiment_id}/json"


class PhoenixService:
    """Serviço para comunicação com o Phoenix"""

    def __init__(self, config: PhoenixConfig):
        self.config = config

    async def _make_graphql_request(
        self, query: str, variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Executa uma requisição GraphQL para o Phoenix"""
        payload = {"query": query, "variables": variables or {}}

        logger.info(f"Fazendo requisição GraphQL para: {self.config.graphql_url}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.graphql_url,
                    json=payload,
                    timeout=self.config.timeout,
                    headers={"Content-Type": "application/json"},
                )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Erro GraphQL. Status: {response.status_code}, Resposta: {response.text}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}",
                )

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao Phoenix: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível conectar ao serviço Phoenix. Verifique se o serviço está no ar. Detalhe: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Erro inesperado no Phoenix: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno no servidor ao processar a requisição. Detalhe: {str(e)}",
            )

    async def get_datasets(self) -> Dict[str, Any]:
        """Busca todos os datasets"""
        query = """
        query DatasetsPageQuery {
          ...DatasetsTable_datasets
        }

        fragment DatasetsTable_datasets on Query {
          datasets(first: 100, sort: {col: createdAt, dir: desc}) {
            edges {
              node {
                id
                name
                description
                metadata
                createdAt
                exampleCount
                experimentCount
                __typename
              }
              cursor
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """
        return await self._make_graphql_request(query)

    async def get_dataset_experiments(self, dataset_id: str) -> Dict[str, Any]:
        """Busca experimentos de um dataset específico"""
        query = """
        query experimentsLoaderQuery($id: GlobalID!) {
          dataset: node(id: $id) {
            __typename
            id
            ... on Dataset {
              name
              description
              exampleCount
              ...ExperimentsTableFragment
            }
          }
        }

        fragment ExperimentsTableFragment on Dataset {
          experimentAnnotationSummaries {
            annotationName
            minScore
            maxScore
          }
          experiments(first: 100) {
            edges {
              experiment: node {
                id
                name
                sequenceNumber
                description
                createdAt
                metadata
                errorRate
                runCount
                averageRunLatencyMs
                project {
                  id
                }
                annotationSummaries {
                  annotationName
                  meanScore
                }
              }
              cursor
              node {
                __typename
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
          id
        }
        """
        return await self._make_graphql_request(query, {"id": dataset_id})

    async def get_dataset_examples(
        self, dataset_id: str, first: int = 1000, after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Busca exemplos de um dataset específico"""
        query = """
        query DatasetExamplesQuery($datasetId: GlobalID!, $first: Int!, $after: String) {
          dataset: node(id: $datasetId) {
            __typename
            ... on Dataset {
              id
              name
              exampleCount
              examples(first: $first, after: $after) {
                edges {
                  example: node {
                    id
                    latestRevision: revision {
                      input
                      output
                      metadata
                    }
                    span {
                      id
                      trace {
                        id
                        traceId
                        project {
                          id
                        }
                      }
                    }
                  }
                  cursor
                }
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
          }
        }
        """
        return await self._make_graphql_request(
            query, {"datasetId": dataset_id, "first": first, "after": after}
        )

    async def get_dataset_name(self, dataset_id: str) -> str:
        """Busca o nome de um dataset específico"""
        query = """
        query GetDatasetName($id: GlobalID!) {
          dataset: node(id: $id) {
            __typename
            id
            ... on Dataset {
              name
            }
          }
        }
        """
        try:
            data = await self._make_graphql_request(query, {"id": dataset_id})
            return data.get("data", {}).get("dataset", {}).get("name") or dataset_id
        except Exception as e:
            logger.warning(f"Não foi possível buscar nome do dataset {dataset_id}: {e}")
            return dataset_id

    async def get_experiment_name(self, dataset_id: str, experiment_id: str) -> str:
        """Busca o nome de um experimento específico"""
        try:
            data = await self.get_dataset_experiments(dataset_id)
            experiments = (
                data.get("data", {})
                .get("dataset", {})
                .get("experiments", {})
                .get("edges", [])
            )

            for edge in experiments:
                experiment = edge.get("experiment", {})
                if experiment.get("id") == experiment_id:
                    experiment_name = experiment.get("name")
                    logger.info(f"Nome do experimento encontrado: {experiment_name}")
                    return experiment_name or experiment_id

            logger.warning(
                f"Experimento {experiment_id} não encontrado no dataset {dataset_id}"
            )
            return experiment_id
        except Exception as e:
            logger.error(f"Erro ao buscar nome do experimento: {str(e)}")
            return experiment_id

    async def get_experiment_json_data(self, experiment_id: str) -> Dict[str, Any]:
        """Busca dados JSON de um experimento específico"""
        url = self.config.experiment_json_url(experiment_id)

        logger.info(f"Fazendo requisição para: {url}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                return json.loads(response.text)
            else:
                logger.error(
                    f"Erro ao buscar dados do experimento. Status: {response.status_code}"
                )
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}",
                )

        except httpx.RequestError as e:
            logger.error(f"Erro de conexão ao Phoenix: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Não foi possível conectar ao serviço Phoenix. Detalhe: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro interno no servidor. Detalhe: {str(e)}"
            )
