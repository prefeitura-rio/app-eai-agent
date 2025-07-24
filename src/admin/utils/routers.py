from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "auth")
TEMPLATE_PATH = os.path.join(STATIC_DIR, "auth.html")


@router.get("/favicon.ico")
async def get_favicon(frontend_manager):
    """Serve o favicon do admin."""
    return frontend_manager.serve_favicon()


@router.get("/auth/{file_path:path}")
def serve_auth_static(file_path: str):
    file_full_path = os.path.join(STATIC_DIR, file_path)
    if not os.path.isfile(file_full_path):
        return HTMLResponse(status_code=404, content="Arquivo não encontrado.")
    return FileResponse(file_full_path)


@router.get("/auth", response_class=HTMLResponse)
def serve_auth_page():
    if not os.path.isfile(TEMPLATE_PATH):
        return HTMLResponse(
            status_code=404, content="Página de autenticação não encontrada."
        )
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)
