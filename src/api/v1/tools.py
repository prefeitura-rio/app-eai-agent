# from fastapi import APIRouter, Depends, Body
# from typing import Optional

# from src.core.security.dependencies import validar_token
# from src.schemas.letta_schema import MessageRequest, MessageResponse
# from src.services.letta.agents.tasks.google_search import google_search

# router = APIRouter(prefix="/letta/tools", tags=["Letta", "Tools"], dependencies=[Depends(validar_token)])

# @router.get("/google_search", name="Busca Google")
# async def google_search(
#     query: str = Query(..., description="Texto da consulta"),
#     model: str = Query("gemini-2.5-pro-preview-03-25", description="Modelo Gemini a ser usado"),
# ):
#     try:
#         gemini_service = GeminiService()
#         actual_query = query

#         system_prompt = ""
#         prompt = {"role": "user", "parts": [{"text": actual_query}]}
        
#         logger.info("Enviando consulta para o Gemini com system_instruction")
#         response, token_usage = await generate_content_async(
#             prompt, model=model, system_instruction=system_prompt
#         )

#         if not response or not response.candidates:
#             raise HTTPException(status_code=500, detail="Falha ao gerar resposta do Gemini")

#         result = response.candidates[0].content.parts[0].text.strip()

#         return {
#             "response": result,
#             "model": model,
#             "token_usage": token_usage,
#         }
#     except Exception as e:
#         logger.error(f"Erro ao gerar resposta do Gemini: {e}")
#         raise HTTPException(status_code=500, detail=f"Erro ao processar a requisição: {str(e)}")