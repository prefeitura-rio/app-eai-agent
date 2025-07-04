import ast
import os
import httpx
import json
import mimetypes

from fastapi import APIRouter, Request, Response, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

from src.config import env
from loguru import logger

# Cria um novo roteador para a seção de experimentos
router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logger.info(f"Diretório estático de experimentos: {STATIC_DIR}")


def replace_api_base_url(html_content: str) -> str:
    if env.USE_LOCAL_API:
        return html_content.replace(
            "{{BASE_API_URL}}",
            "http://localhost:8089/eai-agent",
        )
    else:
        return html_content.replace(
            "{{BASE_API_URL}}",
            "https://services.staging.app.dados.rio/eai-agent",
        )


# Endpoints estáticos DEVEM vir primeiro para evitar conflitos
@router.get("/favicon.ico")
async def get_favicon():
    """
    Serve o favicon do admin para garantir compatibilidade entre local e produção.
    Funciona tanto para /admin/experiments/favicon.ico quanto para /admin/static/favicon.ico
    """
    # Caminho para o favicon do admin (uma pasta acima)
    admin_static_dir = os.path.join(os.path.dirname(BASE_DIR), "static")
    favicon_path = os.path.join(admin_static_dir, "favicon.ico")

    if os.path.exists(favicon_path):
        return FileResponse(
            favicon_path,
            media_type="image/x-icon",
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache por 24 horas
            },
        )
    else:
        logger.error(f"Favicon não encontrado em: {favicon_path}")
        return Response(content="Favicon não encontrado", status_code=404)


@router.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """
    Serve arquivos estáticos com MIME types corretos
    """
    file_full_path = os.path.join(STATIC_DIR, file_path)

    if not os.path.exists(file_full_path):
        logger.error(f"Arquivo estático não encontrado: {file_full_path}")
        return Response(content="Arquivo não encontrado", status_code=404)

    # Determinar MIME type baseado na extensão
    mime_type, _ = mimetypes.guess_type(file_full_path)

    # Forçar MIME types específicos para garantir compatibilidade
    if file_path.endswith(".css"):
        mime_type = "text/css"
    elif file_path.endswith(".js"):
        mime_type = "application/javascript"
    elif file_path.endswith(".html"):
        mime_type = "text/html"
    elif file_path.endswith(".ico"):
        mime_type = "image/x-icon"

    if not mime_type:
        mime_type = "application/octet-stream"

    logger.info(f"Servindo arquivo: {file_path} com MIME type: {mime_type}")

    return FileResponse(
        file_full_path,
        media_type=mime_type,
        headers={
            "Cache-Control": "no-cache, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/auth", response_class=HTMLResponse)
async def get_auth_page(request: Request):
    """
    Retorna a página de autenticação centralizada.
    A URL final será /admin/experiments/auth
    """
    html_path = os.path.join(STATIC_DIR, "auth.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            html_content = replace_api_base_url(html_content=html_content)
            return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar auth.html: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro ao carregar a página de autenticação: {e}</h1>",
            status_code=500,
        )


@router.get("/data")
async def get_datasets_data():
    """
    Endpoint para buscar dados dos datasets do serviço Phoenix.
    A URL final será /admin/experiments/data
    """
    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}graphql"

    payload = {
        "query": """query DatasetsPageQuery {
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
        }""",
        "variables": {},
    }

    logger.info(f"Fazendo requisição GraphQL para: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            logger.error(
                f"Erro ao buscar dados do Phoenix. Status: {response.status_code}, Resposta: {response.text}"
            )
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "detail": f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}"
                },
            )

    except httpx.RequestError as e:
        logger.error(f"Erro de conexão ao tentar acessar o Phoenix em {url}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível conectar ao serviço Phoenix em {phoenix_endpoint}. Verifique se o serviço está no ar e a URL está correta. Detalhe: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro inesperado no proxy para o Phoenix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno no servidor ao processar a requisição. Detalhe: {str(e)}",
        )


@router.get("/", response_class=HTMLResponse)
async def get_datasets_page(request: Request):
    """
    Retorna a página principal de visualização de datasets.
    A URL final será /admin/experiments/
    """
    html_path = os.path.join(STATIC_DIR, "datasets.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            html_content = replace_api_base_url(html_content=html_content)
            return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar datasets.html: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro ao carregar a página de datasets: {e}</h1>",
            status_code=500,
        )


@router.get("/{dataset_id}/data")
async def get_dataset_data(dataset_id: str):
    """
    Endpoint para buscar dados de um dataset específico do serviço Phoenix.
    A URL final será /admin/experiments/{dataset_id}/data
    """

    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}graphql"

    payload = {
        "query": """query experimentsLoaderQuery(
          $id: GlobalID!
        ) {
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
        }""",
        "variables": {"id": dataset_id},
    }

    logger.info(f"Fazendo requisição GraphQL para dataset {dataset_id}: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            logger.error(
                f"Erro ao buscar dados do dataset {dataset_id}. Status: {response.status_code}, Resposta: {response.text}"
            )
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "detail": f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}"
                },
            )

    except httpx.RequestError as e:
        logger.error(f"Erro de conexão ao tentar acessar o Phoenix em {url}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível conectar ao serviço Phoenix em {phoenix_endpoint}. Verifique se o serviço está no ar e a URL está correta. Detalhe: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro inesperado no proxy para o Phoenix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno no servidor ao processar a requisição. Detalhe: {str(e)}",
        )


@router.get("/{dataset_id}/examples")
async def get_dataset_examples(dataset_id: str, first: int = 1000, after: str = None):
    """
    Endpoint para buscar exemplos de um dataset específico do serviço Phoenix.
    A URL final será /admin/experiments/{dataset_id}/examples
    """
    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}graphql"

    payload = {
        "query": """query DatasetExamplesQuery($datasetId: GlobalID!, $first: Int!, $after: String) {
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
        }""",
        "variables": {"datasetId": dataset_id, "first": first, "after": after},
    }

    logger.info(
        f"Fazendo requisição GraphQL para exemplos do dataset {dataset_id}: {url}"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            logger.error(
                f"Erro ao buscar exemplos do dataset {dataset_id}. Status: {response.status_code}, Resposta: {response.text}"
            )
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "detail": f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}"
                },
            )

    except httpx.RequestError as e:
        logger.error(f"Erro de conexão ao tentar acessar o Phoenix em {url}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Não foi possível conectar ao serviço Phoenix em {phoenix_endpoint}. Verifique se o serviço está no ar e a URL está correta. Detalhe: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro inesperado no proxy para o Phoenix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno no servidor ao processar a requisição. Detalhe: {str(e)}",
        )


@router.get("/{dataset_id}/{experiment_id}/data")
async def get_experiment_data(dataset_id: str, experiment_id: str):
    """
    Endpoint para buscar dados de um experimento específico do serviço Phoenix.
    A URL final será /admin/experiments/{dataset_id}/{experiment_id}/data
    """
    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}v1/experiments/{experiment_id}/json"

    logger.info(f"Fazendo proxy da requisição para: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)

        # Repassa o status e o conteúdo da resposta do Phoenix
        if response.status_code == 200:
            response_content = parse_output(json.loads(response.text))
            # Adiciona informações do dataset
            response_content["dataset_id"] = dataset_id
            response_content["experiment_id"] = experiment_id

            # Buscar nome do dataset
            try:
                dataset_name = await get_dataset_name(dataset_id)
                response_content["dataset_name"] = dataset_name
            except Exception as e:
                logger.warning(
                    f"Não foi possível buscar nome do dataset {dataset_id}: {e}"
                )
                response_content["dataset_name"] = dataset_id

            # Buscar nome do experimento
            try:
                experiment_name = await get_experiment_name(dataset_id, experiment_id)
                response_content["experiment_name"] = experiment_name
            except Exception as e:
                logger.warning(
                    f"Não foi possível buscar nome do experimento {experiment_id}: {e}"
                )
                response_content["experiment_name"] = experiment_id

            return JSONResponse(content=response_content)
        else:
            logger.error(
                f"Erro ao buscar dados do Phoenix. Status: {response.status_code}, Resposta: {response.text}"
            )
            # Retorna um erro formatado que o frontend pode exibir
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "detail": f"Erro ao contatar o serviço Phoenix (Status {response.status_code}): {response.text}"
                },
            )

    except httpx.RequestError as e:
        logger.error(f"Erro de conexão ao tentar acessar o Phoenix em {url}: {str(e)}")
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Não foi possível conectar ao serviço Phoenix em {phoenix_endpoint}. Verifique se o serviço está no ar e a URL está correta. Detalhe: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Erro inesperado no proxy para o Phoenix: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno no servidor ao processar a requisição. Detalhe: {str(e)}",
        )


@router.get("/{dataset_id}/{experiment_id}", response_class=HTMLResponse)
async def get_experiment_page(request: Request, dataset_id: str, experiment_id: str):
    """
    Retorna a página de visualização de um experimento específico.
    A URL final será /admin/experiments/{dataset_id}/{experiment_id}
    """
    html_path = os.path.join(STATIC_DIR, "experiment.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            html_content = replace_api_base_url(html_content=html_content)
            # Injeta o dataset_id e experiment_id no HTML
            html_content = html_content.replace("{{DATASET_ID}}", dataset_id)
            html_content = html_content.replace("{{EXPERIMENT_ID}}", experiment_id)
            return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar experiment.html: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro ao carregar a página de experimento: {e}</h1>",
            status_code=500,
        )


@router.get("/{dataset_id}", response_class=HTMLResponse)
async def get_dataset_experiments_page(request: Request, dataset_id: str):
    """
    Retorna a página de experimentos de um dataset específico.
    A URL final será /admin/experiments/{dataset_id}
    """
    html_path = os.path.join(STATIC_DIR, "dataset-experiments.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            html_content = replace_api_base_url(html_content=html_content)
            # Injeta o dataset_id no HTML
            html_content = html_content.replace("{{DATASET_ID}}", dataset_id)
            return HTMLResponse(content=html_content)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar dataset-experiments.html: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro ao carregar a página de experimentos do dataset: {e}</h1>",
            status_code=500,
        )


async def get_dataset_name(dataset_id: str) -> str:
    """
    Busca o nome de um dataset específico do serviço Phoenix.
    """
    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}graphql"

    payload = {
        "query": """query GetDatasetName($id: GlobalID!) {
          dataset: node(id: $id) {
            __typename
            id
            ... on Dataset {
              name
            }
          }
        }""",
        "variables": {"id": dataset_id},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )

    if response.status_code == 200:
        data = response.json()
        dataset_name = data.get("data", {}).get("dataset", {}).get("name")
        return dataset_name or dataset_id
    else:
        return dataset_id


async def get_experiment_name(dataset_id: str, experiment_id: str) -> str:
    """
    Busca o nome de um experimento específico do serviço Phoenix usando a mesma query da página de experimentos do dataset.
    """
    phoenix_endpoint = env.PHOENIX_ENDPOINT
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}graphql"

    # Usar a mesma query que a página de experimentos do dataset usa
    payload = {
        "query": """query experimentsLoaderQuery(
          $id: GlobalID!
        ) {
          dataset: node(id: $id) {
            __typename
            id
            ... on Dataset {
              name
              description
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
        }""",
        "variables": {"id": dataset_id},
    }

    logger.info(f"Buscando nome do experimento {experiment_id} no dataset {dataset_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )

        if response.status_code == 200:
            data = response.json()
            experiments = (
                data.get("data", {})
                .get("dataset", {})
                .get("experiments", {})
                .get("edges", [])
            )

            # Procurar pelo experimento específico
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
        else:
            logger.error(f"Erro ao buscar experimentos: {response.status_code}")
            return experiment_id

    except Exception as e:
        logger.error(f"Erro ao buscar nome do experimento: {str(e)}")
        return experiment_id


def parse_json_strings_recursively(obj):
    """
    Percorre recursivamente um objeto Python (dicionário ou lista) e converte
    qualquer valor de string que seja um JSON válido ou uma representação literal
    de um objeto Python em seu objeto Python correspondente.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = parse_json_strings_recursively(value)
        return obj
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = parse_json_strings_recursively(item)
        return obj
    elif isinstance(obj, str):
        try:
            cleaned_str = obj.strip()
            if cleaned_str.startswith(("{", "[")) and cleaned_str.endswith(("}", "]")):
                data = json.loads(obj)
                return parse_json_strings_recursively(data)
            else:
                return obj
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(obj)
                return parse_json_strings_recursively(data)
            except (ValueError, SyntaxError, TypeError):
                return obj
        except (TypeError, ValueError):
            return obj
    else:
        return obj


# --- Script principal (permanece o mesmo) ---
def parse_output(output):
    processed_output = parse_json_strings_recursively(output)
    if "experiment_metadata" in processed_output[0]["output"]:
        experiment_metadata = processed_output[0]["output"]["experiment_metadata"]
    else:
        experiment_metadata = {}

    for item in processed_output:
        item["example_id_clean"] = item["example_id"].replace("==", "")
        if "experiment_metadata" in item.get("output", {}):
            item["output"].pop("experiment_metadata")
        if "resposta_gpt" in item["output"]["agent_output"]:
            logger.info("resposta_gpt found")
            agent_output = item["output"]["agent_output"]
            new_agent_output = {
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
            item["output"]["agent_output"] = new_agent_output

    final_output = {
        "experiment_metadata": experiment_metadata,
        "experiment": processed_output,
    }
    with open("processed_output.json", "w") as f:
        json.dump(final_output, f, indent=4)
    return final_output
