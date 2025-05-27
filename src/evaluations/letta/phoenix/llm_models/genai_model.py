import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from phoenix.evals.models.base import BaseModel
from phoenix.evals.models.rate_limiters import RateLimiter
from phoenix.evals.templates import MultimodalPrompt
from phoenix.evals.utils import printif

import sys
import os

# Adicionar o diretório raiz do projeto ao path para permitir importações absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
from src.services.llm.gemini_service import gemini_service

logger = logging.getLogger(__name__)


MODEL_TOKEN_LIMIT_MAPPING = {
    "gemini-2.0-flash": 1024,
}


@dataclass
class GenAIModel(BaseModel):
    """
    Modelo baseado no Google GenAI 
        parametrs:
            api_key: str
            default_concurrency: int
            model: str
            temperature: float
            max_tokens: int
            top_p: float
            top_k: int
            stop_sequences: List[str]
            initial_rate_limit: int
            timeout: int
    """

    api_key: Optional[str] = None

    default_concurrency: int = 5

    model: str = "gemini-2.0-flash"
    temperature: float = 0.0
    max_tokens: int = 1024
    top_p: float = 1
    top_k: int = 32
    stop_sequences: List[str] = field(default_factory=list)
    initial_rate_limit: int = 5
    timeout: int = 120

    def __post_init__(self) -> None:
        self._init_client()
        self._init_rate_limiter()

    @property
    def _model_name(self) -> str:
        return self.model

    def reload_client(self) -> None:
        self._init_client()

    def _init_client(self) -> None:
        pass

    def _init_rate_limiter(self) -> None:
        from google.api_core import exceptions
        self._rate_limiter = RateLimiter(
            rate_limit_error=exceptions.ResourceExhausted,
            max_rate_limit_retries=10,
            initial_per_second_request_rate=self.initial_rate_limit,
            enforcement_window_minutes=1,
        )

    @property
    def generation_config(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "stop_sequences": self.stop_sequences,
        }

    def _generate(self, prompt: Union[str, MultimodalPrompt], **kwargs: Dict[str, Any]) -> str:
        kwargs.pop("instruction", None)

        if isinstance(prompt, str):
            prompt = MultimodalPrompt.from_string(prompt)

        @self._rate_limiter.limit
        def _rate_limited_completion(
            prompt: MultimodalPrompt, generation_config: Dict[str, Any], **kwargs: Any
        ) -> Any:
            prompt_str = self._construct_prompt(prompt)
            
            config = {
                "temperature": generation_config.get("temperature", self.temperature),
                "max_output_tokens": generation_config.get("max_output_tokens", self.max_tokens),
                "top_p": generation_config.get("top_p", self.top_p),
                "top_k": generation_config.get("top_k", self.top_k),
            }
            
            if generation_config.get("stop_sequences"):
                config["stop_sequences"] = generation_config.get("stop_sequences")
                
            # Usamos o event loop para executar de forma síncrona
            import asyncio
            
            # Metodo mais simples e seguro de executar código assíncrono em contexto síncrono
            response = asyncio.run(gemini_service.generate_content(
                text=prompt_str,
                model=self.model,
                config=config,
                response_format="raw",
                **{k: v for k, v in kwargs.items() if k not in ["generation_config"]}
            ))
            
            return self._parse_response_candidates(response)

        response = _rate_limited_completion(
            prompt=prompt,
            generation_config=self.generation_config,
            **kwargs,
        )

        return str(response)

    async def _async_generate(
        self, prompt: Union[str, MultimodalPrompt], **kwargs: Dict[str, Any]
    ) -> str:
        kwargs.pop("instruction", None)

        if isinstance(prompt, str):
            prompt = MultimodalPrompt.from_string(prompt)

        @self._rate_limiter.alimit
        async def _rate_limited_completion(
            prompt: MultimodalPrompt, generation_config: Dict[str, Any], **kwargs: Any
        ) -> Any:
            prompt_str = self._construct_prompt(prompt)
            
            # Usar o gemini_service para geração assíncrona
            config = {
                "temperature": generation_config.get("temperature", self.temperature),
                "max_output_tokens": generation_config.get("max_output_tokens", self.max_tokens),
                "top_p": generation_config.get("top_p", self.top_p),
                "top_k": generation_config.get("top_k", self.top_k),
            }
            
            if generation_config.get("stop_sequences"):
                config["stop_sequences"] = generation_config.get("stop_sequences")
                
            try:
                response = await gemini_service.generate_content(
                    text=prompt_str,
                    model=self.model,
                    config=config,
                    response_format="raw",
                    **{k: v for k, v in kwargs.items() if k not in ["generation_config"]}
                )
                
                return self._parse_response_candidates(response)
            except Exception as e:
                printif(self._verbose, f"Erro na geração assíncrona: {str(e)}")
                return f"Erro: {str(e)}"

        response = await _rate_limited_completion(
            prompt=prompt,
            generation_config=self.generation_config,
            **kwargs,
        )

        return str(response)

    def _parse_response_candidates(self, response: Any) -> Any:
        # Estrutura da resposta do gemini_service:
        # response.candidates[0].content.parts[0] para texto
        if hasattr(response, "candidates"):
            if isinstance(response.candidates, list) and len(response.candidates) > 0:
                try:
                    # Nova estrutura do Gemini API
                    if hasattr(response.candidates[0], "content"):
                        if hasattr(response.candidates[0].content, "parts") and response.candidates[0].content.parts:
                            return response.candidates[0].content.parts[0]
                    # Tenta acessar text (estrutura antiga)    
                    elif hasattr(response.candidates[0], "text"):
                        return response.candidates[0].text
                    else:
                        printif(
                            self._verbose, "Não foi possível acessar o conteúdo da resposta."
                        )
                        printif(self._verbose, str(response.candidates[0]))
                        return ""
                except Exception as e:
                    printif(
                        self._verbose, f"Erro ao extrair resposta: {str(e)}"
                    )
                    printif(self._verbose, str(response.candidates[0]))
                    return ""
            else:
                printif(
                    self._verbose,
                    "The 'candidates' attribute of 'response' is either not a list or is empty.",
                )
                printif(self._verbose, str(response))
                return ""
        else:
            printif(self._verbose, "The 'response' object does not have a 'candidates' attribute.")
            return ""

    def _construct_prompt(self, prompt: MultimodalPrompt) -> str:
        return prompt.to_text_only_prompt()
