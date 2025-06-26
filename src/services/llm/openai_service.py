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
                - links: Lista de links com metadados nativos (quando usar web_search)
                  * uri: URL da fonte
                  * title: Título da página
                  * start_index/end_index: Posição da citação no texto
                  * web_search_id: ID da busca realizada
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
                "search_context_size": "medium",  # low, medium, high
                "user_location": {
                    "type": "approximate",
                    "country": "BR",
                    "city": "Rio de Janeiro",
                    "region": "Rio de Janeiro"
                }
            }],
            "tool_choice": {"type": "web_search_preview"},
            "temperature": 0.7, 
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
                "web_search_used": True,
                "raw_response": response  
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
                "web_search_used": False,
                "raw_response": response  
            }

        except Exception as e:
            print(f"Erro ao gerar conteúdo: {e}")
            raise

    def _extract_text_from_response(self, response) -> str:
        """Extrai texto da Responses API conforme estrutura das docs oficiais."""
        try:
            if hasattr(response, 'output_text'):
                return response.output_text
            
            elif hasattr(response, 'output') and hasattr(response.output, 'items'):
                for item in response.output.items:
                    if hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content') and len(item.content) > 0:
                            content_item = item.content[0]
                            if hasattr(content_item, 'text'):
                                return content_item.text
                            elif hasattr(content_item, 'type') and content_item.type == 'output_text':
                                return content_item.text
            
            return str(response)
            
        except Exception as e:
            print(f"Erro ao extrair texto da Responses API: {e}")
            return f"Erro ao extrair texto: {str(e)}"

    def _extract_links_from_response(self, response) -> List[Dict[str, Any]]:
        """Extrai links com metadados da Responses API conforme docs oficiais."""
        links = []
        
        try:
            web_search_id = None
            
            if hasattr(response, 'output') and isinstance(response.output, list):
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'web_search_call':
                        web_search_id = getattr(item, 'id', None)
                        status = getattr(item, 'status', 'unknown')
                        print(f"🔍 Web search call encontrado: {web_search_id} (status: {status})")
                    
                    elif hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content') and len(item.content) > 0:
                            content_item = item.content[0]
                            
                            if hasattr(content_item, 'annotations') and content_item.annotations:
                                for annotation in content_item.annotations:
                                    if hasattr(annotation, 'type') and annotation.type == 'url_citation':
                                        link_data = {
                                            "uri": getattr(annotation, 'url', ''),
                                            "title": getattr(annotation, 'title', None),
                                            "start_index": getattr(annotation, 'start_index', None),
                                            "end_index": getattr(annotation, 'end_index', None),
                                            "web_search_id": web_search_id,
                                            "source": "responses_api_native"
                                        }
                                        
                                        link_data = {k: v for k, v in link_data.items() if v is not None}
                                        links.append(link_data)
            
            elif hasattr(response, 'output') and hasattr(response.output, 'items'):
                for item in response.output.items:
                    if hasattr(item, 'type') and item.type == 'web_search_call':
                        web_search_id = getattr(item, 'id', None)
                        status = getattr(item, 'status', 'unknown')
                        print(f"🔍 Web search call encontrado: {web_search_id} (status: {status})")
                    
                    elif hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content') and len(item.content) > 0:
                            content_item = item.content[0]
                            
                            if hasattr(content_item, 'annotations') and content_item.annotations:
                                for annotation in content_item.annotations:
                                    if hasattr(annotation, 'type') and annotation.type == 'url_citation':
                                        link_data = {
                                            "uri": getattr(annotation, 'url', ''),
                                            "title": getattr(annotation, 'title', None),
                                            "start_index": getattr(annotation, 'start_index', None),
                                            "end_index": getattr(annotation, 'end_index', None),
                                            "web_search_id": web_search_id,
                                            "source": "responses_api_native"
                                        }
                                        
                                        link_data = {k: v for k, v in link_data.items() if v is not None}
                                        links.append(link_data)

            print(f"✅ Links extraídos nativamente: {len(links)}")
            
            if len(links) == 0:
                print("🔍 DEBUG: Estrutura da resposta para análise:")
                if hasattr(response, 'output'):
                    if isinstance(response.output, list):
                        print(f"   output é lista com {len(response.output)} items")
                        for i, item in enumerate(response.output):
                            print(f"   Item {i}: type={getattr(item, 'type', 'N/A')}")
                            if hasattr(item, 'content'):
                                print(f"     content length: {len(item.content) if item.content else 0}")
                                if item.content and len(item.content) > 0:
                                    content = item.content[0]
                                    print(f"     annotations: {hasattr(content, 'annotations')}")
                                    if hasattr(content, 'annotations'):
                                        print(f"     annotations length: {len(content.annotations) if content.annotations else 0}")
                    else:
                        print(f"   output type: {type(response.output)}")
                else:
                    print("   Sem atributo output")
            
        except Exception as e:
            print(f"❌ Erro ao extrair links da Responses API: {e}")
            import traceback
            traceback.print_exc()

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
