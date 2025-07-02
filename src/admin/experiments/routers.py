from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import mimetypes
from loguru import logger


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
    A URL final será /admin/experiments/
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


@router.get("/config")
async def get_experiments_config():
    """
    Endpoint que fornece configurações do backend para o frontend.
    A URL final será /admin/experiments/config
    """
    phoenix_endpoint = os.getenv("PHOENIX_ENDPOINT")
    if not phoenix_endpoint:
        logger.warning(
            "A variável de ambiente PHOENIX_ENDPOINT não está definida. Usando fallback."
        )
        phoenix_endpoint = "http://localhost:8001/"

    return JSONResponse(content={"phoenix_endpoint": phoenix_endpoint})


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


# Comentando o mount padrão para usar endpoint customizado
# router.mount("/static", StaticFiles(directory=STATIC_DIR), name="experiments_static")
