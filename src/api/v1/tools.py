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
            response_format="text_and_links"
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


@router.get("/google_search_raw", name="Busca Google (Resposta Bruta)")
async def google_search_raw_tool(
    query: str = Query(..., description="Texto da consulta"),
):
    try:
        gemini_service = GeminiService()
        response = await gemini_service.generate_content(
            query,
            model="gemini-2.0-flash",
            use_google_search=True,
            response_format="raw"
        )

        if not response:
            raise HTTPException(
                status_code=500, detail="Falha ao gerar resposta do Gemini"
            )
        
        debug_info = {}
        
        debug_info["tipo_resposta"] = str(type(response))
        
        if isinstance(response, dict):
            debug_info["é_dicionário"] = True
            if "response" in response:
                debug_info["contém_chave_response"] = True
                inner_response = response["response"]
                debug_info["tipo_inner_response"] = str(type(inner_response))
                
                if "candidates" in inner_response:
                    debug_info["tem_candidates"] = True
                    debug_info["qtd_candidates"] = len(inner_response["candidates"])
                    
                    if len(inner_response["candidates"]) > 0:
                        candidate = inner_response["candidates"][0]
                        debug_info["tem_grounding_metadata"] = "groundingMetadata" in candidate
                        
                        if "groundingMetadata" in candidate:
                            grounding = candidate["groundingMetadata"]
                            debug_info["tem_chunks"] = "groundingChunks" in grounding
                            
                            if "groundingChunks" in grounding:
                                chunks = grounding["groundingChunks"]
                                debug_info["qtd_chunks"] = len(chunks)
                                
                                links = []
                                for chunk in chunks:
                                    if "web" in chunk and "uri" in chunk["web"]:
                                        links.append({
                                            "uri": chunk["web"]["uri"],
                                            "title": chunk["web"].get("title", "Sem título")
                                        })
                                debug_info["links_extraídos"] = links
                                debug_info["qtd_links"] = len(links)
        else:
            debug_info["é_dicionário"] = False
            debug_info["tem_attr_candidates"] = hasattr(response, "candidates")
            
            if hasattr(response, "candidates"):
                candidates = response.candidates
                debug_info["qtd_candidates"] = len(candidates) if candidates else 0
                
                if candidates and len(candidates) > 0:
                    candidate = candidates[0]
                    debug_info["tem_attr_grounding"] = hasattr(candidate, "groundingMetadata")
                    
                    if hasattr(candidate, "groundingMetadata"):
                        grounding = candidate.groundingMetadata
                        debug_info["tem_attr_chunks"] = hasattr(grounding, "groundingChunks")
                        
                        if hasattr(grounding, "groundingChunks"):
                            chunks = grounding.groundingChunks
                            debug_info["qtd_chunks"] = len(chunks) if chunks else 0
                            
                            links = []
                            if chunks:
                                for chunk in chunks:
                                    if hasattr(chunk, "web") and hasattr(chunk.web, "uri"):
                                        links.append({
                                            "uri": chunk.web.uri,
                                            "title": chunk.web.title if hasattr(chunk.web, "title") else "Sem título"
                                        })
                            debug_info["links_extraídos"] = links
                            debug_info["qtd_links"] = len(links)
        
        if not isinstance(response, dict):
            response_str = str(response)
            return {
                "response_debug": debug_info,
                "response_raw": response_str
            }
        
        return {
            "response_debug": debug_info,
            "response_raw": response
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
            prompt,
            model="gemini-2.0-flash",
            response_format="text_only"
        )
        
        if not response or response.get("texto") is None:
            raise HTTPException(
                status_code=500, detail="Falha ao gerar resumo"
            )
            
        return {
            "resumo": response["texto"]
        }
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )
