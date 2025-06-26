import re
from typing import Optional, Union, Dict, Any
from pathlib import Path
from openai import AsyncAzureOpenAI
import src.config.env as env


class GPTService:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=env.OPENAI_API_KEY,
            api_version="2025-01-01-preview",
            azure_endpoint=env.OPENAI_URL
        )
        self.deployment = "gpt-4o"

    async def generate_content(
        self,
        text: str,
        # image: Optional[Union[str, Path, bytes]] = None,
        config: Optional[Dict[str, Any]] = None,
        response_format: str = "raw"
    ):
        messages = [{"role": "user", "content": text}]

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                **(config or {})
            )

            if response_format == "raw":
                return response
            elif response_format == "text_only":
                return self._extract_text(response)
            elif response_format == "text_and_links":
                return self._extract_text_and_links(response)
            else:
                return response
        except Exception as e:
            print(f"Erro ao gerar conteúdo com Azure OpenAI: {e}")
            raise

    def _extract_text(self, response) -> Dict[str, Optional[str]]:
        try:
            message = response.choices[0].message
            return {"texto": message.content if message else None}
        except Exception as e:
            print(f"Erro ao extrair texto: {e}")
            return {"texto": None}

    def _extract_text_and_links(self, response) -> Dict[str, Any]:
        resultado = self._extract_text(response)
        texto = resultado.get("texto") or ""
        urls = list(dict.fromkeys(re.findall(r'https?://[^\s\]\)]+', texto)))
        links = [{"uri": url.strip(), "title": None} for url in urls]
        resultado["links"] = links
        return resultado


##### testando
async def main():
    gpt = GPTService()
    prompt = "Explique o que é inteligência artificial generativa e cite fontes com links."
    resp = await gpt.generate_content(prompt, response_format="text_and_links")
    print(resp)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())