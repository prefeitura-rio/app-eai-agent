from fastapi import APIRouter, Depends, HTTPException

from src.core.security.dependencies import validar_token
from src.services.rmi.api import RMIClient
from typing import Dict, List
from src.utils.log import logger


router = APIRouter(
    prefix="/rmi",
    tags=["RMI"],
    dependencies=[Depends(validar_token)],
)


@router.get("/whitelist", response_model=Dict[str, List[str]])
async def get_whitelist():
    """
    Obtém a whitelist agrupada por grupo.

    Returns:
        Dict[str, List[str]]: Whitelist agrupada por group_name
        Formato: {"group_name": ["phone1", "phone2", ...]}
    """
    client = RMIClient()

    try:
        logger.info("Iniciando busca da whitelist")
        whitelist = await client.get_whitelist_grouped_by_group()

        if whitelist is None:
            raise HTTPException(
                status_code=500, detail="Erro interno ao obter whitelist"
            )

        return whitelist

    except Exception as e:
        logger.error(f"Erro ao obter whitelist: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter whitelist: {str(e)}"
        )
    finally:
        await client.close()
