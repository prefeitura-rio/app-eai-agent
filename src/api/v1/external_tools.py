from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger

from src.core.security.dependencies import validar_token
from src.services.geocoding.pluscode_service import (
    get_pluscode_equipments,
    get_category_equipments,
)

router = APIRouter(
    prefix="/external/tools",
    tags=["External Tools"],
    dependencies=[Depends(validar_token)],
)

@router.get("/equipaments", name="Equipamentos")
async def get_equipaments(
    address: str = Query(..., description="Endereço"),
):
    try:

        response = await get_pluscode_equipments(address=address)

        if not response:
            raise HTTPException(status_code=500, detail="Falha ao gerar resumo")

        return {"equipamentos": response}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/equipaments_category", name="Categoria dos Equipamentos")
async def get_category():
    try:
        response = await get_category_equipments()
        if not response:
            raise HTTPException(status_code=500, detail="Falha ao gerar resumo")

        return {"categorias": response}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )