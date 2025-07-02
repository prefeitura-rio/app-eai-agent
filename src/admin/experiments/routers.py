from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
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
    html_path = os.path.join(STATIC_DIR, "experiments.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {html_path}")
        return Response(content="Página não encontrada.", status_code=404)
    except Exception as e:
        logger.error(f"Erro ao carregar experiments.html: {str(e)}")
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


# Monta o diretório estático. A URL final será /admin/experiments/static/
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="experiments_static")
