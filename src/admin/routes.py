from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logger.info(f"Diretório de arquivos estáticos: {STATIC_DIR}")
logger.info(f"Arquivo index.html: {os.path.join(STATIC_DIR, 'index.html')}")

@router.get("/", response_class=HTMLResponse)
async def get_admin_panel(request: Request):
    """
    Retorna a página principal do painel administrativo.
    A autenticação será gerenciada pelo frontend.
    """
    try:
        with open(os.path.join(STATIC_DIR, "index.html"), "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Erro ao carregar index.html: {str(e)}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Admin Panel</title>
        </head>
        <body>
            <h1>Erro ao carregar painel administrativo</h1>
            <p>Detalhes: {str(e)}</p>
        </body>
        </html>
        """)

@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

router.mount("/static", StaticFiles(directory=STATIC_DIR), name="admin_static") 