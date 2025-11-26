import requests
import httpx
from typing import Dict, List, Optional
from src.config import env
from src.utils.log import logger


class RMIClient:
    def __init__(self, timeout: int = 300):
        self.issuer = env.CIDADAO_ISSUER
        self.client_id = env.CIDADAO_CLIENT_ID
        self.client_secret = env.CIDADAO_CLIENT_SECRET
        self.base_url = env.CIDADAO_API_BASE_URL
        self.timeout = timeout

        # Obtém token na inicialização
        token = self._get_access_token()

        headers = (
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            if token
            else {"Content-Type": "application/json"}
        )

        self._client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, timeout=self.timeout
        )

    def _get_access_token(self) -> Optional[str]:
        """Obtém o access token"""
        url = f"{self.issuer}/protocol/openid-connect/token"

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "profile email",
        }

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get("access_token")

            if access_token:
                logger.info("Token obtido com sucesso!")
                return access_token
            else:
                logger.error("access_token não encontrado na resposta")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter token: {e}")
            return None

    async def get_whitelist(self, page: int = 1, per_page: int = 10) -> Optional[Dict]:
        """Faz uma requisição GET para o endpoint whitelist com paginação"""
        try:
            params = {"page": page, "per_page": per_page}
            response = await self._client.get("/admin/beta/whitelist", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Erro na requisição '/admin/beta/whitelist': {e}")
            return None

    async def get_all_whitelist(self) -> List[Dict]:
        """Obtém todos os itens da whitelist percorrendo todas as páginas"""
        all_items = []
        page = 1

        while True:
            result = await self.get_whitelist(page=page)
            if not result or not result.get("whitelisted"):
                break
            all_items.extend(result["whitelisted"])
            pagination = result.get("pagination", {})
            total_pages = pagination.get("total_pages", 0)
            current_page = pagination.get("page", 1)
            # Se chegou na última página ou não há mais páginas
            if current_page >= total_pages or len(result["whitelisted"]) == 0:
                break

            page += 1

        return all_items

    async def get_whitelist_grouped_by_group(self) -> Dict[str, List[str]]:
        """Obtém whitelist agrupada por group_name"""
        all_items = await self.get_all_whitelist()
        grouped = {}

        for item in all_items:
            group_name = item.get("group_name")
            phone_number = item.get("phone_number")

            if group_name and phone_number:
                if group_name not in grouped:
                    grouped[group_name] = []
                grouped[group_name].append(phone_number.replace("+", ""))

        return grouped

    async def close(self):
        """Fecha o cliente"""
        await self._client.aclose()


async def main():
    """Função principal"""
    # Usando o novo client
    client = RMIClient()
    try:
        # Obter agrupado por grupo
        grouped_whitelist = await client.get_whitelist_grouped_by_group()
        print(grouped_whitelist)

    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
