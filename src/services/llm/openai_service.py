import os
import re
from typing import Dict, Any, Optional, Union, List
import asyncio
from pathlib import Path
import base64
from openai import AsyncOpenAI
import src.config.env as env


class OpenAIService:
    def __init__(self):
        """Inicializa o cliente OpenAI direto (não Azure)."""
        self.api_key = env.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)

    def get_client(self):
        """Retorna a instância do cliente OpenAI."""
        return self.client

    async def generate_content(
        self,
        text: str,
        image: Optional[Union[str, Path, bytes]] = None,
        model: str = "gpt-4o",
        use_web_search: bool = False,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando OpenAI direto com web search nativo opcional.

        Args:
            text: Texto/pergunta a ser processado
            image: Caminho da imagem, bytes da imagem ou URL da imagem (opcional)
            model: Nome do modelo a ser usado (padrão: gpt-4.1)
            use_web_search: Usar web search nativo da OpenAI (padrão: False)
            config: Configurações adicionais para a geração de conteúdo (opcional)

        Returns:
            Dict contendo:
                - resposta: Texto gerado pelo modelo
                - links: Lista de links com metadados (quando usar web_search)
                  * uri: URL da fonte
                  * title: Título da página
                - model_used: Modelo usado na geração
                - web_search_used: Se web search foi usado
        """
        
        if use_web_search:
            return await self._generate_with_web_search(text, image, model, config)
        else:
            return await self._generate_without_web_search(text, image, model, config)

    async def _generate_with_web_search(
        self,
        text: str,
        image: Optional[Union[str, Path, bytes]] = None,
        model: str = "gpt-4o",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        request_config = {
            "model": model,
            "input": text,
            "tools": [{
                "type": "web_search_preview",
                "search_context_size": "medium",
                "user_location": {
                    "type": "approximate",
                    "country": "BR",
                    "city": "Rio de Janeiro",
                    "region": "Rio de Janeiro"
                }
            }],
            "max_output_tokens": 4000,
        }

        if config:
            request_config.update(config)

        try:
            response = await self.client.responses.create(**request_config)
            
            return {
                "resposta": self._extract_text_from_response(response),
                "links": self._extract_links_from_response(response),
                "model_used": model,
                "web_search_used": True
            }

        except Exception as e:
            print(f"Erro ao usar Responses API: {e}")
            raise

    async def _generate_without_web_search(
        self,
        text: str,
        image: Optional[Union[str, Path, bytes]] = None,
        model: str = "gpt-4o",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        
        messages = []
        
        content = []
        content.append({"type": "text", "text": text})

        if image:
            try:
                image_content = self._process_image(image)
                if image_content:
                    content.append(image_content)
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

        messages.append({"role": "user", "content": content})

        generation_config = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000,
        }

        if config:
            generation_config.update(config)

        try:
            response = await self.client.chat.completions.create(**generation_config)
            
            return {
                "resposta": self._extract_text_from_chat_completion(response),
                "links": [],
                "model_used": model,
                "web_search_used": False
            }

        except Exception as e:
            print(f"Erro ao gerar conteúdo: {e}")
            raise

    def _extract_text_from_response(self, response) -> str:
        """Extrai texto da Responses API conforme documentação oficial."""
        try:
            # Primeira tentativa: output_text direto (conforme docs)
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text.strip()
            
            # Segunda tentativa: buscar na estrutura output
            if hasattr(response, 'output') and isinstance(response.output, list):
                for item in response.output:
                    if getattr(item, 'type', None) == 'message':
                        text = self._extract_text_from_message_item(item)
                        if text:
                            return text.strip()
            
            # Terceira tentativa: buscar em output.items
            elif hasattr(response, 'output') and hasattr(response.output, 'items'):
                for item in response.output.items:
                    if getattr(item, 'type', None) == 'message':
                        text = self._extract_text_from_message_item(item)
                        if text:
                            return text.strip()
            
            # Se chegou até aqui, não conseguiu extrair texto
            return ""
            
        except Exception as e:
            print(f"Erro ao extrair texto da Responses API: {e}")
            return ""
    
    def _extract_text_from_message_item(self, item) -> str:
        """Extrai texto de um item do tipo 'message'."""
        try:
            if not hasattr(item, 'content') or not item.content:
                return ""
            
            for content_item in item.content:
                if hasattr(content_item, 'text') and content_item.text:
                    return content_item.text
            
            return ""
        except Exception:
            return ""

    def _extract_links_from_response(self, response) -> List[Dict[str, Any]]:
        """Extrai links com metadados da Responses API conforme documentação oficial."""
        links = []
        
        try:
            web_search_id = None
            
            # Processa output como lista
            if hasattr(response, 'output') and isinstance(response.output, list):
                links.extend(self._process_output_items(response.output))
            
            # Processa output.items
            elif hasattr(response, 'output') and hasattr(response.output, 'items'):
                links.extend(self._process_output_items(response.output.items))
            
        except Exception as e:
            print(f"Erro ao extrair links da Responses API: {e}")

        return links
    
    def _process_output_items(self, items) -> List[Dict[str, Any]]:
        """Processa itens do output para extrair links."""
        links = []
        web_search_id = None
        
        try:
            for item in items:
                item_type = getattr(item, 'type', None)
                
                # Captura ID da busca web
                if item_type == 'web_search_call':
                    web_search_id = getattr(item, 'id', None)
                
                # Extrai links das mensagens
                elif item_type == 'message':
                    message_links = self._extract_links_from_message(item, web_search_id)
                    links.extend(message_links)
        
        except Exception as e:
            print(f"Erro ao processar items do output: {e}")
        
        return links
    
    def _extract_links_from_message(self, message_item, web_search_id: str = None) -> List[Dict[str, Any]]:
        """Extrai links de um item de mensagem."""
        links = []
        
        try:
            if not hasattr(message_item, 'content') or not message_item.content:
                return links
            
            for content_item in message_item.content:
                if hasattr(content_item, 'annotations') and content_item.annotations:
                    for annotation in content_item.annotations:
                        if getattr(annotation, 'type', None) == 'url_citation':
                            link_data = {
                                "uri": getattr(annotation, 'url', ''),
                                "title": getattr(annotation, 'title', None)
                            }
                            
                            # Remove campos vazios/None
                            link_data = {k: v for k, v in link_data.items() if v}
                            
                            if link_data.get("uri"):
                                links.append(link_data)
        
        except Exception as e:
            print(f"Erro ao extrair links da mensagem: {e}")
        
        return links

    def _extract_text_from_chat_completion(self, response) -> str:
        """Extrai texto da Chat Completions API."""
        try:
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and choice.message:
                    return choice.message.content
            return "Erro: não foi possível extrair texto da resposta"
        except Exception as e:
            print(f"Erro ao extrair texto: {e}")
            return f"Erro: {str(e)}"

    def _process_image(self, image: Union[str, Path, bytes]) -> Optional[Dict[str, Any]]:
        """Processa a imagem para o formato esperado pela API OpenAI."""
        try:
            if isinstance(image, (str, Path)) and os.path.isfile(str(image)):
                mime_type = self._get_mime_type(str(image))
                with open(image, "rb") as f:
                    image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                }
            elif isinstance(image, bytes):
                image_base64 = base64.b64encode(image).decode('utf-8')
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            elif isinstance(image, str) and (image.startswith('http') or image.startswith('data:')):
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": image
                    }
                }
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return None

    def _get_mime_type(self, file_path: str) -> str:
        """Determina o tipo MIME com base na extensão do arquivo."""
        extension = os.path.splitext(file_path)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }
        return mime_types.get(extension, "image/jpeg")
      
openai_service = OpenAIService()
