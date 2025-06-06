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

        return response
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


@router.get("/final_summary", name="Resumo final")
async def final_summary_tool(
    context: str = Query(..., description="Contexto da consulta"),
):
    try:
        gemini_service = GeminiService()
        prompt = f"""
        Com base no contexto fornecido, gere um resumo claro e conciso destacando os pontos principais.
        O resumo deve ser bem estruturado e fácil de entender.
        
        Contexto: {context}
        """

        response = await gemini_service.generate_content(
            prompt, model="gemini-2.0-flash", response_format="text_only"
        )

        if not response or response.get("texto") is None:
            raise HTTPException(status_code=500, detail="Falha ao gerar resumo")

        return {"resumo": response["texto"]}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )
