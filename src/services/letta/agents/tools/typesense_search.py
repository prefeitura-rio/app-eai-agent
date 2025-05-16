import httpx
from fastapi import Query, HTTPException
from loguru import logger
import src.config.env as env

async def typesense_search(
  query: str = Query(..., description="Texto da consulta"),
  collections: str = Query(..., description="Coleções a serem buscadas"),
  limit: int = Query(..., description="Limite de resultados")
):
  try:
    base_url = env.TYPESENSE_CLIENT_API_URL
    endpoint = f"{base_url}/search/hybrid"
    
    params = {
        "q": query,
        "cs": collections,
        "limit": limit
    }
    
    headers = {
        "Authorization": f"Bearer {env.TYPESENSE_CLIENT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=10.0
        )
        
        response.raise_for_status()
        
        return response.json()
        
  except httpx.HTTPStatusError as e:
    logger.error(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
    raise HTTPException(
      status_code=e.response.status_code, detail=f"Erro na requisição ao Typesense: {e.response.text}"
    )
  except httpx.RequestError as e:
    logger.error(f"Erro de requisição: {str(e)}")
    raise HTTPException(
      status_code=500, detail=f"Erro ao conectar ao Typesense: {str(e)}"
    )
  except Exception as e:
    logger.error(f"Erro: {e}")
    raise HTTPException(
      status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
    )