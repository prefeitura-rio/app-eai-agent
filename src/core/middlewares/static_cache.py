from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import re


class NoCacheStaticFilesMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona cabeçalhos Cache-Control para recursos estáticos
    evitando a necessidade de limpar o cache do navegador manualmente.
    """

    def __init__(
        self, app: ASGIApp, static_url: str = "/admin/static", max_age: int = 0
    ):
        super().__init__(app)
        self.static_url = static_url
        self.max_age = max_age
        self.static_pattern = re.compile(f"^{static_url}")

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Verifica se o caminho corresponde ao nosso padrão de recursos estáticos
        if self.static_pattern.match(request.url.path):
            # Adiciona headers para evitar caching
            response.headers["Cache-Control"] = f"no-cache, max-age={self.max_age}"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
