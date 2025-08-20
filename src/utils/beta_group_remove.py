import requests
import pandas as pd
import json
import sys
import argparse
from typing import Dict, List, Optional
from src.config.env import (
    WHITELIST_API_BASE_URL_STAGING,
    WHITELIST_ISSUER_STAGING,
    WHITELIST_CLIENT_ID_STAGING,
    WHITELIST_CLIENT_SECRET_STAGING,
    WHITELIST_API_BASE_URL_PROD,
    WHITELIST_ISSUER_PROD,
    WHITELIST_CLIENT_ID_PROD,
    WHITELIST_CLIENT_SECRET_PROD,
    WHITELIST_GOOGLE_SHEET
)


def get_environment_config(env: str) -> Dict[str, str]:
    """
    Retorna a configuração para o ambiente especificado.
    
    Args:
        env (str): Ambiente ("staging" ou "production")
    
    Returns:
        Dict[str, str]: Configuração do ambiente
    
    Raises:
        ValueError: Se o ambiente não for válido
    """
    if env == "staging":
        return {
            "api_base_url": WHITELIST_API_BASE_URL_STAGING,
            "issuer": WHITELIST_ISSUER_STAGING,
            "client_id": WHITELIST_CLIENT_ID_STAGING,
            "client_secret": WHITELIST_CLIENT_SECRET_STAGING
        }
    elif env == "production":
        return {
            "api_base_url": WHITELIST_API_BASE_URL_PROD,
            "issuer": WHITELIST_ISSUER_PROD,
            "client_id": WHITELIST_CLIENT_ID_PROD,
            "client_secret": WHITELIST_CLIENT_SECRET_PROD
        }
    else:
        raise ValueError(f"Ambiente inválido: {env}. Use 'staging' ou 'production'.")


def validate_environment_config(config: Dict[str, str]) -> None:
    """
    Valida se todas as configurações necessárias estão presentes.
    
    Args:
        config (Dict[str, str]): Configuração do ambiente
    
    Raises:
        ValueError: Se alguma configuração estiver faltando
    """
    required_keys = ["api_base_url", "issuer", "client_id", "client_secret"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        raise ValueError(f"Configurações faltando: {missing_keys}. Verifique suas variáveis de ambiente.")


class BetaGroupRemover:
    def __init__(self, issuer: str, client_id: str, client_secret: str, api_base_url: str):
        self.issuer = issuer
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base_url = api_base_url
        self.access_token = None
    
    def authenticate(self) -> bool:
        """Autentica na API e obtém o access token"""
        url = f"{self.issuer}/protocol/openid-connect/token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "profile email"
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
            raise ValueError("Token de acesso não disponível. Execute authenticate() primeiro.")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_whitelist(self) -> Optional[Dict]:
        """
        Obtém a lista completa de números na whitelist com paginação
        """
        all_whitelisted = []
        page = 1
        per_page = 100
        total_count = None
        
        print(f"📥 Buscando whitelist completa (páginas de {per_page} registros)...")
        
        while True:
            url = f"{self.api_base_url}/whitelist"
            params = {
                "page": page,
                "per_page": per_page
            }
            
            try:
                response = requests.get(url, headers=self.get_headers(), params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Primeira vez que obtemos os dados, salvamos informações de paginação
                if total_count is None:
                    total_count = data.get("total_count", 0)
                    print(f"📊 Total de registros na whitelist: {total_count}")
                
                # Adiciona os registros desta página
                page_whitelisted = data.get("whitelisted", [])
                all_whitelisted.extend(page_whitelisted)
                
                print(f"📥 Página {page}: {len(page_whitelisted)} registros (total acumulado: {len(all_whitelisted)})")
                
                # Para o loop se:
                # 1. Não há mais registros nesta página
                # 2. Já obtivemos todos os registros esperados
                if (len(page_whitelisted) == 0 or 
                    len(page_whitelisted) < per_page or 
                    (total_count and len(all_whitelisted) >= total_count)):
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Erro ao obter whitelist (página {page}): {e}")
                if page == 1:
                    # Se falhou na primeira página, retorna None
                    return None
                else:
                    # Se falhou em páginas posteriores, retorna o que já temos
                    print(f"⚠️ Continuando com {len(all_whitelisted)} registros obtidos até agora...")
                    break
        
        print(f"✅ Whitelist completa obtida: {len(all_whitelisted)} registros totais")
        
        # Retorna no mesmo formato esperado pelo resto do código
        return {
            "total_count": len(all_whitelisted),
            "whitelisted": all_whitelisted,
            "pagination": {
                "page": 1,
                "per_page": len(all_whitelisted),
                "total": len(all_whitelisted),
                "total_pages": 1
            }
        }
    
    def get_numbers_by_group(self, group_name: str) -> List[str]:
        """
        Obtém todos os números de um grupo específico
        """
        whitelist_data = self.get_whitelist()
        if not whitelist_data:
            return []
        
        numbers = []
        for entry in whitelist_data.get("whitelisted", []):
            if entry.get("group_name") == group_name:
                phone_number = entry.get("phone_number")
                if phone_number:
                    # Remove o '+' se existir
                    clean_number = phone_number.replace('+', '')
                    numbers.append(clean_number)
        
        return numbers
    
    def list_groups_with_counts(self) -> Dict[str, int]:
        """
        Lista todos os grupos e quantos números cada um tem
        """
        whitelist_data = self.get_whitelist()
        if not whitelist_data:
            return {}
        
        groups_count = {}
        for entry in whitelist_data.get("whitelisted", []):
            group_name = entry.get("group_name", "Sem grupo")
            if group_name not in groups_count:
                groups_count[group_name] = 0
            groups_count[group_name] += 1
        
        return groups_count
    
    def remove_numbers_from_whitelist(self, phone_numbers: List[str]) -> bool:
        """
        Remove números de telefone da whitelist
        """
        url = f"{self.api_base_url}/whitelist/bulk-remove"
        
        payload = {
            "phone_numbers": phone_numbers
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            response.raise_for_status()
            
            print(f"✅ {len(phone_numbers)} números removidos da whitelist com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao remover números da whitelist: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta do servidor: {e.response.text}")
            return False


def normalize_numbers(clean_number: str) -> List[str]:
    """
    Normaliza número de telefone brasileiro para sempre ter '55' + DDD + número,
    e gera SEMPRE duas versões: com e sem o '9' após o DDD.
    """
    if not clean_number.startswith("55"):
        clean_number = "55" + clean_number

    # Remove prefixo 55 para analisar DDD e número
    local_number = clean_number[2:]

    # Se o número já tem 9 depois do DDD, cria versão sem ele
    if len(local_number) >= 11 and local_number[2] == "9":
        with_nine = clean_number
        without_nine = "55" + local_number[:2] + local_number[3:]
    else:
        # Caso contrário, cria versão com 9 inserido depois do DDD
        without_nine = clean_number
        with_nine = "55" + local_number[:2] + "9" + local_number[2:]

    return list({with_nine, without_nine})


def parse_phone_numbers(numbers_input: str) -> List[str]:
    """
    Processa entrada de números de telefone (separados por vírgula, espaço ou quebra de linha)
    """
    # Substitui quebras de linha e vírgulas por espaços
    cleaned_input = numbers_input.replace('\n', ' ').replace(',', ' ')
    
    # Divide por espaços e filtra números válidos
    raw_numbers = cleaned_input.split()
    
    normalized_numbers = []
    for number in raw_numbers:
        # Remove espaços, hífens, parênteses e outros caracteres
        clean_number = ''.join(filter(str.isdigit, str(number)))
        if len(clean_number) >= 10:  # Número mínimo válido
            normalized_numbers.extend(normalize_numbers(clean_number))
        else:
            print(f"⚠️ Número inválido ignorado: {number}")
    
    return list(set(normalized_numbers))


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Script para remover números da whitelist beta"
    )
    parser.add_argument(
        "--env",
        choices=["staging", "production"],
        default="staging",
        help="Ambiente a ser usado (default: staging)"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--group",
        type=str,
        help="Nome do grupo para remover todos os números"
    )
    group.add_argument(
        "--numbers",
        type=str,
        help="Lista de números separados por vírgula ou espaço para remover"
    )
    group.add_argument(
        "--list-groups",
        action="store_true",
        help="Lista todos os grupos e quantos números cada um tem"
    )
    
    args = parser.parse_args()
    
    print("=== Beta Group Remove Script ===")
    print(f"Ambiente: {args.env}")
    
    try:
        # Obtém e valida configuração do ambiente
        config = get_environment_config(args.env)
        validate_environment_config(config)
        print(f"✅ Configuração do ambiente '{args.env}' carregada com sucesso")
        
        # Mostra configuração mascarada para debug (sem mostrar secrets)
        print(f"  API Base URL: {config['api_base_url']}")
        print(f"  Issuer: {config['issuer']}")
        print(f"  Client ID: {config['client_id']}")
        print("  Client Secret: [MASKED]")
        
    except ValueError as e:
        print(f"❌ Erro na configuração: {e}")
        sys.exit(1)
    
    # Inicializa o removedor com a configuração do ambiente
    remover = BetaGroupRemover(
        config["issuer"],
        config["client_id"],
        config["client_secret"],
        config["api_base_url"]
    )
    
    # 1. Autentica na API
    print("\n1. Autenticando na API...")
    if not remover.authenticate():
        print("Falha na autenticação. Encerrando.")
        sys.exit(1)
    
    # 2. Executa a ação solicitada
    if args.list_groups:
        print("\n2. Listando grupos e contagens...")
        groups = remover.list_groups_with_counts()
        
        if not groups:
            print("Nenhum grupo encontrado na whitelist.")
        else:
            print(f"\n📋 Grupos encontrados na whitelist:")
            total_numbers = 0
            for group_name, count in sorted(groups.items()):
                print(f"  📱 {group_name}: {count} números")
                total_numbers += count
            print(f"\n📊 Total: {total_numbers} números em {len(groups)} grupos")
    
    elif args.group:
        print(f"\n2. Removendo todos os números do grupo '{args.group}'...")
        
        # Obtém números do grupo
        numbers_to_remove = remover.get_numbers_by_group(args.group)
        
        if not numbers_to_remove:
            print(f"❌ Grupo '{args.group}' não encontrado ou não possui números.")
            sys.exit(1)
        
        print(f"📱 Encontrados {len(numbers_to_remove)} números no grupo '{args.group}':")
        for number in sorted(numbers_to_remove)[:10]:  # Mostra apenas os primeiros 10
            print(f"  - +{number}")
        
        if len(numbers_to_remove) > 10:
            print(f"  ... e mais {len(numbers_to_remove) - 10} números")
        
        # Confirma remoção
        print(f"\n⚠️ ATENÇÃO: Você está prestes a remover {len(numbers_to_remove)} números do grupo '{args.group}' no ambiente {args.env.upper()}!")
        confirm = input("Digite 'CONFIRMAR' para prosseguir: ")
        
        if confirm != "CONFIRMAR":
            print("❌ Operação cancelada.")
            sys.exit(1)
        
        # Remove números
        if remover.remove_numbers_from_whitelist(numbers_to_remove):
            print(f"🎉 Grupo '{args.group}' removido com sucesso!")
        else:
            print(f"❌ Falha ao remover grupo '{args.group}'.")
    
    elif args.numbers:
        print(f"\n2. Removendo números específicos...")
        
        # Processa números
        numbers_to_remove = parse_phone_numbers(args.numbers)
        
        if not numbers_to_remove:
            print("❌ Nenhum número válido encontrado.")
            sys.exit(1)
        
        print(f"📱 Números que serão removidos ({len(numbers_to_remove)}):")
        for number in sorted(numbers_to_remove):
            print(f"  - {number}")
        
        # Confirma remoção
        print(f"\n⚠️ ATENÇÃO: Você está prestes a remover {len(numbers_to_remove)} números no ambiente {args.env.upper()}!")
        confirm = input("Digite 'CONFIRMAR' para prosseguir: ")
        
        if confirm != "CONFIRMAR":
            print("❌ Operação cancelada.")
            sys.exit(1)
        
        # Remove números
        if remover.remove_numbers_from_whitelist(numbers_to_remove):
            print(f"🎉 {len(numbers_to_remove)} números removidos com sucesso!")
        else:
            print(f"❌ Falha ao remover números.")


if __name__ == "__main__":
    main()
