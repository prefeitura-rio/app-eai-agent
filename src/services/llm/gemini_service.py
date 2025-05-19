import os
from typing import Dict, Any, Optional, Union
import asyncio
from pathlib import Path
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

import src.config.env as env

class GeminiService:
    def __init__(self):
        """Inicializa o cliente Gemini com as configurações do ambiente."""
        self.api_key = env.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)
        
    def get_client(self):
        """Retorna a instância do cliente Gemini."""
        return self.client
        
    async def generate_content(
        self,
        text: str,
        image: Optional[Union[str, Path, bytes]] = None,
        model: str = "gemini-2.0-flash",
        config: Optional[Dict[str, Any]] = None,
        use_google_search: bool = False,
        response_format: str = "raw"
    ):
        """
        Gera conteúdo usando o modelo Gemini de forma assíncrona.
        
        Args:
            text: Texto a ser processado
            image: Caminho da imagem, bytes da imagem ou URL da imagem (opcional)
            model: Nome do modelo a ser usado (padrão: gemini-2.0-flash)
            config: Configurações adicionais para a geração de conteúdo (opcional)
            use_google_search: Ativar pesquisa Google para fundamentar respostas (padrão: False)
            response_format: Formato de resposta (raw, text_only, text_and_links)
            
        Returns:
            Resposta do modelo Gemini no formato especificado
        """
        contents = []
        
        content_parts = []
        content_parts.append({"text": text})
        
        if image:
            try:
                if isinstance(image, (str, Path)) and os.path.isfile(str(image)):
                    mime_type = self._get_mime_type(str(image))
                    with open(image, "rb") as f:
                        image_bytes = f.read()
                    content_parts.append({"inline_data": {"mime_type": mime_type, "data": image_bytes}})
                elif isinstance(image, bytes):
                    content_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image}})
                elif isinstance(image, str):
                    content_parts.append({"inline_data": {"mime_type": "image/jpeg", "uri": image}})
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")
        
        contents = [{"parts": content_parts}]
        
        generation_config = None
        if config:
            generation_config = GenerateContentConfig(**config)
        else:
            generation_config = GenerateContentConfig()
        
        if use_google_search:
            google_search_tool = Tool(
                google_search=GoogleSearch()
            )
            
            if generation_config.tools:
                generation_config.tools.append(google_search_tool)
            else:
                generation_config.tools = [google_search_tool]
                
            generation_config.response_modalities = ["TEXT"]
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generation_config
            )
        )
        
        if response_format == "raw":
            return response
        elif response_format == "text_only":
            return self._extract_text(response)
        elif response_format == "text_and_links":
            return self._extract_text_and_links(response)
        else:
            return response
            
    def _extract_text(self, response):
        texto = None
        if (response.get("candidates") and 
            len(response["candidates"]) > 0 and 
            response["candidates"][0].get("content") and 
            response["candidates"][0]["content"].get("parts") and 
            len(response["candidates"][0]["content"]["parts"]) > 0 and 
            response["candidates"][0]["content"]["parts"][0].get("text")):
            texto = response["candidates"][0]["content"]["parts"][0]["text"]
        
        return {"texto": texto}
        
    def _extract_text_and_links(self, response):
        resultado = self._extract_text(response)
        
        links = []
        if (response.get("groundingMetadata") and 
            response["groundingMetadata"].get("groundingChunks")):
            for chunk in response["groundingMetadata"]["groundingChunks"]:
                if chunk.get("web") and chunk["web"].get("uri"):
                    links.append({
                        "uri": chunk["web"]["uri"],
                        "title": chunk["web"].get("title")
                    })
        
        resultado["links"] = links
        return resultado
    
    def _get_mime_type(self, file_path: str) -> str:
        """Determina o tipo MIME com base na extensão do arquivo."""
        extension = os.path.splitext(file_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp"
        }
        return mime_types.get(extension, "application/octet-stream")

gemini_service = GeminiService()
