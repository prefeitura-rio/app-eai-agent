from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from src.core.security.dependencies import validar_token
from src.services.letta.agents.tools.typesense_search import typesense_search
from src.services.llm.gemini_service import GeminiService


router = APIRouter(
    prefix="/letta/tools",
    tags=["Letta Tools"],
    dependencies=[Depends(validar_token)],
)


@router.get("/google_search", name="Busca Google")
async def google_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        gemini_service = GeminiService()
        response = await gemini_service.generate_content(
            query,
            model="gemini-2.0-flash",
            use_google_search=True,
            response_format="text_and_links",
        )

        if not response or response.get("texto") is None:
            raise HTTPException(
                status_code=500, detail="Falha ao gerar resposta do Gemini"
            )

        # Filtra links permitidos e limita a 10 resultados relevantes
        # Permitimos apenas domínios oficiais de interesse
        ALLOWED_PREFIXES = (
            "https://carioca.rio/servicos/",
            "https://www.1746.rio/hc/pt-br/articles/",
            "https://assistenciasocial.prefeitura.rio/",
            "https://prefeitura.rio/",
        )

        EXCLUDE_KEYWORDS = ("termo-de-uso", "privacidade", "faq", "politica")

        def allowed(u: str) -> bool:
            if not u:
                return False
            if not any(u.startswith(p) for p in ALLOWED_PREFIXES):
                return False
            lowered = u.lower()
            return not any(k in lowered for k in EXCLUDE_KEYWORDS)

        links = response.get("links", [])
        links_filtrados = [l for l in links if allowed(l.get("uri"))][:10]
        response["links"] = links_filtrados

        return response
    except Exception as e:
        logger.error(f"Erro ao gerar resposta do Gemini: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/public_services_grounded_search", name="Busca Serviços Públicos")
async def public_services_grounded_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        collections = "1746,carioca-digital"
        limit = 10
        raw_response = await typesense_search(query, collections, limit)

        # Converte resposta em lista simples de links
        resultado_lista = []

        if isinstance(raw_response, dict):
            if "hits" in raw_response:
                for h in raw_response.get("hits", []):
                    doc = h.get("document", {}) if isinstance(h, dict) else {}
                    url = doc.get("url") or doc.get("link")
                    title = doc.get("title") or doc.get("headline")
                    if url:
                        resultado_lista.append({"uri": url, "title": title})
            elif "result" in raw_response:
                for item in raw_response.get("result", []):
                    url = item.get("url") or item.get("link_acesso")
                    title = item.get("titulo") or item.get("title")
                    if url:
                        resultado_lista.append({"uri": url, "title": title})

        return {"links": resultado_lista[:limit]}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )