import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

from src.api import router as api_router
from src.admin import router as admin_router
from src.core.middlewares.logging import LoggingMiddleware
from src.db import Base, engine

Base.metadata.create_all(bind=engine)

logger.add(
    "logs/api_{time}.log",
    rotation="1 day",
    retention="1 day",
    level="INFO",
    backtrace=True,
    diagnose=True,
)

app = FastAPI(
    title="Agentic Search API",
    description="API que gerencia os fluxos e ferramentas dos agentes de IA da Prefeitura do Rio de Janeiro",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentação",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

admin_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin/static")
app.mount("/admin/static", StaticFiles(directory=admin_static_dir), name="admin_static_direct")

app.include_router(api_router)
app.include_router(admin_router)
