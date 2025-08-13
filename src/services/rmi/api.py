import requests
import pandas as pd
import json
import sys
from typing import Dict, List, Optional
from src.config import env


class BetaGroupManager:
    def __init__(self):
        self.issuer = env.CIDADAO_ISSUER
        self.client_id = env.CIDADAO_CLIENT_ID
        self.client_secret = env.CIDADAO_CLIENT_SECRET
        self.api_base_url = env.CIDADAO_API_BASE_URL
        self.access_token = None

    def authenticate(self) -> bool:
        """Autentica na API e obtém o access token"""
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
            self.access_token = token_data.get("access_token")

            if not self.access_token:
                print("Erro: access_token não encontrado na resposta")
                return False

            print("Autenticação realizada com sucesso!")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Erro na autenticação: {e}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna os headers com autorização"""
        if not self.access_token:
            raise ValueError(
                "Token de acesso não disponível. Execute authenticate() primeiro."
            )

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def list_groups(self) -> Optional[List[Dict]]:
        """Lista todos os grupos existentes"""
        url = f"{self.api_base_url}/groups"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            data = response.json()
            groups = data.get("groups", [])

            return groups

        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar grupos: {e}")
            return None

    def white_list(self) -> Optional[List[Dict]]:
        """Lista todos os grupos existentes"""
        url = f"{self.api_base_url}/whitelist"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()

            data = response.json()

            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar grupos: {e}")
            return None


def main():
    """Função principal"""
    print("=== Beta Group Insert Script ===")

    # Inicializa o gerenciador
    manager = BetaGroupManager()
    manager.authenticate()
    r = manager.white_list()
    print(r)


if __name__ == "__main__":
    main()
