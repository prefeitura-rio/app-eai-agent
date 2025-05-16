from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from src.core.security.dependencies import validar_token
from src.services.letta.agents.tools.typesense_search import typesense_search
from src.services.llm.gemini_service import GeminiService

router = APIRouter(
    prefix="/letta/tools",
    tags=["Letta", "Tools"],
    dependencies=[Depends(validar_token)],
)

@router.get("/google_search", name="Busca Google")
async def google_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        gemini_service = GeminiService()
        actual_query = query
        response = await gemini_service.generate_content(
            actual_query,
            model="gemini-2.0-flash",
            use_google_search=True,
        )

        if not response:
            raise HTTPException(
                status_code=500, detail="Falha ao gerar resposta do Gemini"
            )
        return {
            "response": response,
        }
    except Exception as e:
        logger.error(f"Erro ao gerar resposta do Gemini: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/typesense_search", name="Busca Typesense")
async def typesense_search_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        collections = "1746,carioca-digital"
        limit = 10
        response = await typesense_search(query, collections, limit)
        return response
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )