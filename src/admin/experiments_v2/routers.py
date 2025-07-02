from fastapi import APIRouter, Request, Response, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import os
import mimetypes
from loguru import logger
import httpx
import json

# Cria um novo roteador para a seção de experimentos
router = APIRouter()

# O BASE_DIR agora aponta para /admin/experiments/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logger.info(f"Diretório estático de experimentos: {STATIC_DIR}")


@router.get("/", response_class=HTMLResponse)
async def get_experiments_page(request: Request):
    """
    Retorna a página principal de visualização de experimentos.
    A URL final será /admin/experiments_v2/
    """
    html_path = os.path.join(STATIC_DIR, "experiment.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar experiment.html: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Erro ao carregar a página de experimentos: {e}</h1>",
            status_code=500,
        )


@router.get("/data")
async def get_experiment_data(
    id: str = Query(..., description="O ID do experimento para buscar.")
):
    """
    Endpoint proxy para buscar dados de um experimento do serviço Phoenix.
    Evita problemas de Mixed Content no frontend.
    A URL final será /admin/experiments_v2/data?id=...
    """
    phoenix_endpoint = os.getenv("PHOENIX_ENDPOINT", "http://localhost:8001/")
    if not phoenix_endpoint.endswith("/"):
        phoenix_endpoint += "/"

    url = f"{phoenix_endpoint}v1/experiments/{id}/json"

    logger.info(f"Fazendo proxy da requisição para: {url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)

        # Repassa o status e o conteúdo da resposta do Phoenix
        if response.status_code == 200:
            response_content = parse_output(json.loads(response.text))
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


import json
import ast


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
    experiment_metadata = processed_output[0]["output"]["experiment_metadata"]
    for item in processed_output:
        if "experiment_metadata" in item.get("output", {}):
            item["output"].pop("experiment_metadata")

    final_output = {
        "experiment_metadata": experiment_metadata,
        "experiment": processed_output,
    }

    return final_output
