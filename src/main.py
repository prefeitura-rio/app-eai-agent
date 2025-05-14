import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from loguru import logger
import os

from src.api import router as api_router
from src.core.middlewares.logging import LoggingMiddleware

logger.add(
    "logs/api_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    backtrace=True,
    diagnose=True,
)

app = FastAPI(
    title="Agentic Search API",
    description="API para busca agêntica utilizando Letta",
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

app.include_router(api_router)

def start_dev_server():
    """Inicia o servidor de desenvolvimento."""
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8089,
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    start_dev_server()
