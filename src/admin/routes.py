from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger

from src.config import env
from src.core.security.dependencies import validar_token

router = APIRouter()

# Diretório onde estão os arquivos estáticos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Log do caminho dos arquivos estáticos
logger.info(f"Diretório de arquivos estáticos: {STATIC_DIR}")
logger.info(f"Arquivo index.html: {os.path.join(STATIC_DIR, 'index.html')}")

# Rota principal do painel admin que serve o HTML
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

# Rota para servir o arquivo favicon
@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

# Configurar rotas para servir arquivos estáticos
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static") 