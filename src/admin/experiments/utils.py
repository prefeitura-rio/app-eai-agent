import ast
import os
import httpx
import json
import random

import mimetypes
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from loguru import logger

from fastapi import HTTPException, HTTPException
from fastapi.responses import HTMLResponse, FileResponse


class FrontendManager:
    """Gerencia o serviço de arquivos estáticos e a renderização de templates HTML."""

    def __init__(
        self,
        static_dir: str,
        admin_static_dir: str,
        use_local_api: bool = False,
        base_url_local: str = "http://localhost:8089/eai-agent",
        base_url_staging: str = "https://services.staging.app.dados.rio/eai-agent",
    ):
        self.static_dir = static_dir
        self.admin_static_dir = admin_static_dir
        self.use_local_api = use_local_api
        self.base_url_local = base_url_local
        self.base_url_staging = base_url_staging

    def _replace_api_base_url(self, html_content: str) -> str:
        """Substitui a URL base da API no conteúdo HTML."""
        base_url = self.base_url_local if self.use_local_api else self.base_url_staging
        return html_content.replace("{{BASE_API_URL}}", base_url)

    def _get_mime_type(self, file_path: str) -> str:
        """Determina o MIME type correto para um arquivo."""
        mime_type, _ = mimetypes.guess_type(file_path)

        # Forçar MIME types específicos
        if file_path.endswith(".css"):
            return "text/css"
        elif file_path.endswith(".js"):
            return "application/javascript"
        elif file_path.endswith(".html"):
            return "text/html"
        elif file_path.endswith(".ico"):
            return "image/x-icon"

        return mime_type or "application/octet-stream"

    def serve_file(
        self, file_path: str, cache_control: str = "no-cache, max-age=0"
    ) -> FileResponse:
        """Serve um arquivo estático com headers apropriados."""
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        mime_type = self._get_mime_type(file_path)  # Usar o método interno

        logger.info(f"Servindo arquivo: {file_path} com MIME type: {mime_type}")

        return FileResponse(
            file_path,
            media_type=mime_type,
            headers={
                "Cache-Control": cache_control,
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    def serve_static_file(self, file_path: str) -> FileResponse:
        """Serve arquivo do diretório estático principal."""
        full_path = os.path.join(self.static_dir, file_path)
        return self.serve_file(full_path)

    def serve_favicon(self) -> FileResponse:
        """Serve o favicon do admin."""
        favicon_path = os.path.join(self.admin_static_dir, "favicon.ico")
        return self.serve_file(favicon_path, cache_control="public, max-age=86400")

    def render_html_page(
        self, template_name: str, replacements: Dict[str, str] = None
    ) -> HTMLResponse:
        """Renderiza uma página HTML com substituições opcionais."""
        html_path = os.path.join(self.static_dir, template_name)

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Aplicar substituições
            html_content = self._replace_api_base_url(
                html_content
            )  # Usar o método interno

            if replacements:
                for key, value in replacements.items():
                    html_content = html_content.replace(f"{{{{{key}}}}}", value)

            return HTMLResponse(content=html_content)

        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {html_path}")
            raise HTTPException(status_code=404, detail="Página não encontrada")
        except Exception as e:
            logger.error(f"Erro ao carregar {template_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao carregar a página: {e}"
            )


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
                {"tool_return": {"text": "", "sources": agent_output["fontes"]}}
            ],
            "ordered": [
                {
                    "type": "tool_return_message",
                    "message": {
                        "tool_return": {
                            "text": "",
                            "sources": agent_output["fontes"],
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
        self, processed_data: Dict[str, Any], number_of_random_experiments: int = None
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
                "model_response": item.get("output", {})
                .get("agent_output", {})
                .get("grouped", {})
                .get("assistant_messages", {})[0]
                .get("content", {}),
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
