from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger
from typing import List, Optional

from src.core.security.dependencies import validar_token
from src.services.geocoding.pluscode_service import (
    get_pluscode_coords_equipments,
    get_category_equipments,
    get_tematic_instructions_for_equipments,
)

router = APIRouter(
    prefix="/external/tools",
    tags=["External Tools"],
    dependencies=[Depends(validar_token)],
)


@router.get("/equipments", name="Equipamentos")
async def get_equipaments(
    address: str = Query(..., description="Endereço"),
    categories: Optional[List[str]] = Query(
        default=[],
        description="Categorias dos equipamentos",
    ),
):
    try:
        response = await get_pluscode_coords_equipments(
            address=address, categories=categories
        )
        if response == []:
            raise HTTPException(
                status_code=500,
                detail="Nao foi possivel encontrar equipamentos para endereço/categoria(s) informado(s)",
            )
        if not response:
            raise HTTPException(status_code=500, detail="Falha ao buscar equipamentos")
        return {"equipamentos": response}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get(
    "/equipments_instructions",
    name="Instruções para utilização dos equipamentos",
)
async def get_equipments_instructions():
    try:
        response = await get_tematic_instructions_for_equipments()
        if not response:
            raise HTTPException(status_code=500, detail="Falha ao buscar instruções")

        return response
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )


@router.get("/equipments_category", name="Categoria dos Equipamentos")
async def get_category():
    try:
        response = await get_category_equipments()
        if not response:
            raise HTTPException(status_code=500, detail="Falha ao buscar categorias")

        return {"categorias": response}
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a requisição: {str(e)}"
        )
