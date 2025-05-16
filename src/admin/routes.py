from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import os

from src.config import env
from src.core.security.dependencies import validar_token

router = APIRouter()

# Diretório onde estão os arquivos estáticos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Rota principal do painel admin que serve o HTML
@router.get("/", response_class=HTMLResponse)
async def get_admin_panel(request: Request, token: str = Depends(validar_token)):
    """
    Retorna a página principal do painel administrativo.
    Requer autenticação com token.
    """
    with open(os.path.join(STATIC_DIR, "index.html"), "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Rota para servir o arquivo favicon
@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

# Configurar rotas para servir arquivos estáticos
router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static") 