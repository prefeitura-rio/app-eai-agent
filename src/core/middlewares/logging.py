import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import uuid

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requisições HTTP.
    
    Registra detalhes da requisição como método, caminho, tempo de processamento,
    código de status e identificador único da requisição.
    """
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Log da requisição recebida
        logger.info(f"Requisição iniciada: {request.method} {request.url.path} - ID: {request_id}")
        
        try:
            response = await call_next(request)
            
            # Calcula tempo de processamento
            process_time = time.time() - start_time
            
            # Log da resposta
            logger.info(
                f"Requisição finalizada: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Tempo: {process_time:.4f}s - "
                f"ID: {request_id}"
            )
            
            return response
        except Exception as e:
            # Log de erro
            logger.error(
                f"Erro na requisição: {request.method} {request.url.path} - "
                f"Erro: {str(e)} - "
                f"ID: {request_id}"
            )
            raise 