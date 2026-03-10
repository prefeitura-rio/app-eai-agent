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
    
    if not WHITELIST_GOOGLE_SHEET:
        raise ValueError("WHITELIST_GOOGLE_SHEET não configurado. Verifique suas variáveis de ambiente.")


class BetaGroupManager:
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
            print(f"O token é {self.access_token}")
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
    
    def list_groups(self) -> Optional[List[Dict]]:
        """Lista todos os grupos existentes"""
        url = f"{self.api_base_url}/groups"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            data = response.json()
            groups = data.get("groups", [])
            
            if groups:
                print(f"Encontrados {len(groups)} grupos:")
                for group in groups:
                    print(f"  - {group['name']} (ID: {group['id']})")
            else:
                print("Nenhum grupo encontrado.")

            return groups
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar grupos: {e}")
            return None
    
    def find_group_by_name(self, group_name: str) -> Optional[Dict]:
        """Procura um grupo pelo nome"""
        groups = self.list_groups()
        if not groups:
            return None
        
        for group in groups:
            if group["name"] == group_name:
                return group
        
        return None
    
    def create_group(self, group_name: str) -> Optional[Dict]:
        """Cria um novo grupo"""
        url = f"{self.api_base_url}/groups"
        
        payload = {"name": group_name}
        
        try:
            response = requests.post(url, json=payload, headers=self.get_headers())
            response.raise_for_status()
            
            group_data = response.json()
            print(f"Grupo '{group_name}' criado com sucesso! ID: {group_data['id']}")
            
            return group_data
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao criar grupo: {e}")
            return None
    
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
                # print(self.get_headers())
                # print(response.text)
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
    
    def log_existing_numbers_by_group(self):
        """
        Mostra quais números estão cadastrados em cada grupo
        """
        print("\n--- Números cadastrados na whitelist por grupo ---")
        
        whitelist_data = self.get_whitelist()
        if not whitelist_data:
            print("Não foi possível obter a whitelist atual.")
            return {}
        
        whitelisted = whitelist_data.get("whitelisted", [])
        total_count = whitelist_data.get("total_count", 0)
        
        print(f"Total de números na whitelist: {total_count}")
        
        # Agrupa números por grupo
        groups_numbers = {}
        for entry in whitelisted:
            group_name = entry.get("group_name", "Sem grupo")
            phone_number = entry.get("phone_number")
            
            if group_name not in groups_numbers:
                groups_numbers[group_name] = []
            
            if phone_number:
                groups_numbers[group_name].append(phone_number)
        
        # Mostra números por grupo
        for group_name, numbers in groups_numbers.items():
            print(f"\n📱 Grupo '{group_name}': {len(numbers)} números")
            for number in sorted(numbers):
                print(f"  - {number}")
        
        if not groups_numbers:
            print("Nenhum número encontrado na whitelist.")
        
        return groups_numbers
    
    def get_existing_numbers_set(self) -> set:
        """
        Retorna um set com todos os números já cadastrados na whitelist
        """
        existing_numbers = set()
        whitelist_data = self.get_whitelist()

        if not whitelist_data:
            return existing_numbers
        
        for entry in whitelist_data.get("whitelisted", []):
            phone_number = entry.get("phone_number")
            if phone_number:
                clean_number = ''.join(filter(str.isdigit, str(phone_number)))
                if len(clean_number) >= 10:
                    for norm_num in normalize_numbers(clean_number):
                        existing_numbers.add(norm_num)
        
        return existing_numbers

    def add_numbers_to_group(self, group_id, phone_numbers):
        """
        Adiciona números de telefone a um grupo específico
        """
        url = f"{self.api_base_url}/whitelist/bulk-add"
        
        payload = {
            "group_id": group_id,
            "phone_numbers": phone_numbers
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            print(f"Números adicionados ao grupo {group_id} com sucesso")
            return True  # Retorna True em caso de sucesso
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao adicionar números ao grupo: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta do servidor: {e.response.text}")
            return False  # Retorna False em caso de erro


def download_google_sheets_csv(sheet_url: str) -> Optional[pd.DataFrame]:
    """Baixa dados do Google Sheets como CSV"""
    try:
        # Extrai o sheet ID da URL
        if "spreadsheets/d/" in sheet_url:
            # Formato: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}#gid={GID}
            sheet_id = sheet_url.split("/spreadsheets/d/")[1].split("/")[0]
            
            # Extrai o GID se existir
            gid = "0"  # GID padrão
            if "gid=" in sheet_url:
                gid = sheet_url.split("gid=")[1].split("#")[0].split("&")[0]
            
            # Constrói a URL de exportação CSV
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        else:
            # Fallback para URLs diferentes
            csv_url = sheet_url.replace("/edit", "/export?format=csv")
        
        print(f"URL de download: {csv_url}")
        print(f"Baixando dados do Google Sheets...")
        
        df = pd.read_csv(csv_url)
        
        print(f"Dados baixados com sucesso! {len(df)} registros encontrados.")
        print(f"Colunas: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"Erro ao baixar dados do Google Sheets: {e}")
        return None

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


def main(env: str = "production"):
    """
    Função principal - processa grupos dinamicamente baseado na coluna 'group' do Google Sheets
    
    Args:
        env (str): Ambiente a ser usado ("staging" ou "production"). Default: "staging"
    """
    print("=== Beta Group Insert Script ===")
    print(f"Ambiente: {env}")
    print("Este script cria grupos dinamicamente baseado na coluna 'group' do Google Sheets")
    
    try:
        # Obtém e valida configuração do ambiente
        config = get_environment_config(env)
        validate_environment_config(config)
        print(f"✅ Configuração do ambiente '{env}' carregada com sucesso")
        
        # Mostra configuração mascarada para debug (sem mostrar secrets)
        print(f"  API Base URL: {config['api_base_url']}")
        print(f"  Issuer: {config['issuer']}")
        print(f"  Client ID: {config['client_id']}")
        print("  Client Secret: [MASKED]")
        
    except ValueError as e:
        print(f"❌ Erro na configuração: {e}")
        sys.exit(1)
    
    # Inicializa o gerenciador com a configuração do ambiente
    manager = BetaGroupManager(
        config["issuer"],
        config["client_id"],
        config["client_secret"],
        config["api_base_url"]
    )
    
    # 1. Autentica na API
    print("\n1. Autenticando na API...")
    if not manager.authenticate():
        print("Falha na autenticação. Encerrando.")
        sys.exit(1)

    # 2. Verifica números já cadastrados na whitelist
    print("\n2. Verificando números já cadastrados na whitelist...")
    existing_numbers_by_group = manager.log_existing_numbers_by_group()
    existing_numbers_set = manager.get_existing_numbers_set()
    print(f"Total de números únicos já cadastrados: {len(existing_numbers_set)}")

    # 3. Baixa dados do Google Sheets
    print("\n3. Baixando dados do Google Sheets...")
    df = download_google_sheets_csv(WHITELIST_GOOGLE_SHEET)
    if df is None or df.empty:
        print("Falha ao baixar dados do Google Sheets. Encerrando.")
        sys.exit(1)
    
    # 4. Valida dados baixados
    print(f"\n4. Validando dados baixados...")
    print(f"Total de registros: {len(df)}")
    
    # Verifica se as colunas necessárias existem
    required_columns = ['whatsapp', 'nome', 'group']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Erro: Colunas obrigatórias não encontradas: {missing_columns}")
        print(f"Colunas disponíveis: {list(df.columns)}")
        sys.exit(1)
    
    # Remove linhas vazias
    df = df.dropna(subset=['whatsapp', 'group'])
    print(f"Registros válidos após limpeza: {len(df)}")
    
    if df.empty:
        print("Nenhum registro válido encontrado. Encerrando.")
        sys.exit(1)
    
    print("Primeiros registros:")
    print(df.head())
    
    # 5. Processa cada grupo único
    unique_groups = df['group'].unique()
    print(f"\n5. Encontrados {len(unique_groups)} grupos únicos: {list(unique_groups)}")
    
    for group_name in unique_groups:
        print(f"\n--- Processando grupo: '{group_name}' ---")
        
        # Filtra dados do grupo atual
        group_df = df[df['group'] == group_name]
        print(f"Registros no grupo '{group_name}': {len(group_df)}")
        
        # Verifica se o grupo já existe
        print(f"Verificando se o grupo '{group_name}' já existe...")
        existing_group = manager.find_group_by_name(group_name)
        
        if existing_group:
            print(f"Grupo '{group_name}' já existe (ID: {existing_group['id']})")
            group_id = existing_group['id']
        else:
            # Cria o grupo se não existir
            print(f"Criando grupo '{group_name}'...")
            new_group = manager.create_group(group_name)
            if not new_group:
                print(f"Falha ao criar grupo '{group_name}'. Pulando para o próximo.")
                continue
            group_id = new_group['id']
        
        # Processa números do grupo
        phone_numbers = group_df['whatsapp'].astype(str).tolist()
        names = group_df['nome'].astype(str).tolist()
        
        # Cria um mapeamento de número original para nome
        number_to_name = {}
        for i, number in enumerate(phone_numbers):
            clean_number = ''.join(filter(str.isdigit, str(number)))
            if len(clean_number) >= 10:
                if clean_number not in number_to_name:
                    number_to_name[clean_number] = names[i] if i < len(names) else "Nome não informado"
        
        # Validação e normalização dos números
        all_normalized_numbers = []
        number_to_original = {}  # Mapeia número normalizado para número original
        for number, name in number_to_name.items():
            # Remove espaços, hífens, parênteses e outros caracteres
            normalized_numbers = normalize_numbers(number)
            all_normalized_numbers.extend(normalized_numbers)
            for norm_num in normalized_numbers:
                number_to_original[norm_num] = number
        
        if not all_normalized_numbers:
            print(f"Nenhum número válido encontrado no grupo '{group_name}'. Pulando.")
            continue
        
        # Remove duplicatas dos números normalizados
        unique_normalized_numbers = list(set(all_normalized_numbers))
        
        # Filtra números que já estão na whitelist
        new_numbers = [num for num in unique_normalized_numbers if num not in existing_numbers_set]
        already_exists = [num for num in unique_normalized_numbers if num in existing_numbers_set]
        
        print(f"📊 Estatísticas do grupo '{group_name}':")
        print(f"  - Números únicos após normalização: {len(unique_normalized_numbers)}")
        print(f"  - Números já cadastrados: {len(already_exists)}")
        print(f"  - Números novos para cadastrar: {len(new_numbers)}")
        
        if already_exists:
            print(f"📱 Números já cadastrados (serão ignorados):")
            for num in sorted(already_exists):
                original_num = number_to_original.get(num, num)
                name = number_to_name.get(original_num, "Nome não encontrado")
                print(f"  - {num} ({name})")
        
        if not new_numbers:
            print(f"✅ Todos os números do grupo '{group_name}' já estão cadastrados. Nada a fazer.")
            continue
        
        print(f"📱 Números que serão cadastrados:")
        for num in sorted(new_numbers):
            original_num = number_to_original.get(num, num)
            name = number_to_name.get(original_num, "Nome não encontrado")
            print(f"  - {num} ({name})")
        
        # Adiciona apenas os números novos ao grupo
        if manager.add_numbers_to_group(group_id, new_numbers):
            print(f"✅ Grupo '{group_name}' processado com sucesso!")
            print(f"  ID: {group_id}")
            print(f"  Números novos adicionados: {len(new_numbers)}")
            print(f"  Números que já existiam: {len(already_exists)}")
            
            # Atualiza o set de números existentes para os próximos grupos
            existing_numbers_set.update(new_numbers)
        else:
            print(f"❌ Falha ao adicionar números ao grupo '{group_name}'.")
    
    print(f"\n🎉 Script executado! Processados {len(unique_groups)} grupos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script para inserir grupos beta dinamicamente baseado no Google Sheets"
    )
    parser.add_argument(
        "--env",
        choices=["staging", "production"],
        default="staging",
        help="Ambiente a ser usado (default: staging)"
    )
    
    args = parser.parse_args()
    main(args.env)