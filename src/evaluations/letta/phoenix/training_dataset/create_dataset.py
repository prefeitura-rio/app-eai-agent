import requests
from dotenv import load_dotenv
load_dotenv()

#####
# Verifica se o Typesense está rodando e acessível na URL especificada
#####

try:
    r = requests.get("https://staging.typesense.dados.rio:443/health", timeout=10)
    print(r.text)
except Exception as e:
    print(e)

import typesense
import csv

# Configuração do client
client = typesense.Client({
    "nodes": [{
        "host": "staging.typesense.dados.rio",
        "port": "443", # "8108",
        "protocol": "https"
    }],
    "api_key": os.getenv("TYPESENSE_STAGING_BEARER_API_KEY"),
    "connection_timeout_seconds": 15
})

collections = client.collections.retrieve()
for col in collections:
    print(col['name'])

#####
# Exportando dados de todas as collections do Typesense para CSV
#####

# schema das collections https://github.com/prefeitura-rio/typesense-client/blob/1f74c44521f996af5c1fb2c096caac0525d499f3/app/utils/ingest/schemas.py
# collections disponíveis: https://github.com/prefeitura-rio/typesense-client/blob/a223f87ed833b672e944b480cb043fbe4c8bf03f/app/config/base.py#L1/

# import csv

# collections_name = ["carioca-digital", "1746"]

# # Parâmetros da busca
# query_params = {
#     "q": "*",
#     "query_by": "titulo",     # Use qualquer desde que ele sempra exista no dataset
#     "per_page": 250,
#     "page": 1
# }

# for collection_name in collections_name:
#     all_docs = []

#     while True:
#         response = client.collections[collection_name].documents.search(query_params)
#         hits = response['hits']

#         if not hits:
#             break

#         for hit in hits:
#             all_docs.append(hit['document'])

#         query_params["page"] += 1

#     print(f"Total de documentos exportados: {len(all_docs)}")

#     # Extrair cabeçalhos (campos) únicos
#     fieldnames = set()
#     for doc in all_docs:
#         fieldnames.update(doc.keys())
#     fieldnames = sorted(fieldnames)

#     with open(f"exported_typesense_{collection_name}_data.csv", mode="w", newline="", encoding="utf-8") as csv_file:
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         for doc in all_docs:
#             writer.writerow(doc)

#     print(f"Arquivo CSV salvo como 'exported_typesense_{collection_name}_data.csv'")

######
# Lendo o CSV exportado para análise
######

import pandas as pd

df = pd.read_csv(f"exported_typesense_{1746}_data.csv", encoding="utf-8").drop(columns=["embedding", "ultima_atualizacao", "url", "tipo"])
print(df.head(10))

#####
# Gerando as perguntas
#####

import google.generativeai as genai
from tqdm import tqdm

import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

token=os.getenv("GEMINI_API_KEY")

tqdm.pandas()

genai.configure(api_key=token)  # Obtida em: https://ai.google.dev/

# def generate_questions(row):
#     prompt = f"""Gere 5 perguntas sobre o serviço da prefeitura a seguir como se fosse um morador da cidade com problemas e traga na resposta apenas as perguntas em uma lista sem numeração ou formatação.
#     Titulo : {row['titulo']}.
#     Descrição: {row['descricao_texto_normalizado']}
#     Mais Informações: {row['informacoes_complementares']}
#     Prazo: {row['prazo_esperado']}
#     {f"Custo: {row['custo_do_servico']}" if 'custo_do_servico' in row else ''}
#     """
#     model = genai.GenerativeModel('gemini-2.0-flash')
#     response = model.generate_content(prompt)
#     # print("response", response)
#     return response.text.split("\n")[:5]  # Pega as 5 primeiras linhas


# collections_name = ["carioca-digital", "1746"]
# for collection_name in collections_name:
#     drop_columns = ["embedding", "link_acesso", "ultima_atualizacao", "url", "tipo", "id_carioca_digital"] if collection_name == "carioca-digital" else ["embedding", "ultima_atualizacao", "url", "tipo"]
#     df = pd.read_csv(f"exported_typesense_{collection_name}_data.csv", encoding="utf-8").drop(columns=drop_columns)
#     df['perguntas_geradas'] = df.progress_apply(generate_questions, axis=1)
#     df.to_csv(f"perguntas_baseadas_no_{collection_name}.csv", index=False)

#####
# Gerando as respostas
#####

import ast

# Configurações do modelo Generative AI
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


# MODEL_NAME = "gemini-2.5-flash-preview-05-20" # demorado demais, 20seg por pergunta
MODEL_NAME = "gemini-2.0-flash"

try:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        safety_settings=safety_settings,
        generation_config=generation_config
    )
except Exception as e:
    print(f"Erro ao inicializar o modelo Gemini '{MODEL_NAME}': {e}")
    print("Verifique se o nome do modelo está correto e se você tem acesso a ele.")
    print("Você pode tentar 'gemini-1.5-flash-latest' ou 'gemini-pro'.")
    exit()


def generate_ideal_response(row_data, question_text):
    """
    Gera uma resposta ideal para uma pergunta específica baseada nos dados de um serviço.
    """
    titulo = row_data.get('titulo', 'N/A')
    descricao = row_data.get('descricao_texto_normalizado', 'N/A')
    informacoes_comp = row_data.get('informacoes_complementares', 'N/A')
    prazo = row_data.get('prazo_esperado', 'N/A')
    custo_key = 'custo_do_servico' # Chave original
    if custo_key not in row_data: # Tentativa com possível variação no nome da coluna
        custo_key = 'custo'
    custo = row_data.get(custo_key, None)


    contexto_servico = f"Título do Serviço: {titulo}\n"
    contexto_servico += f"Descrição: {descricao}\n"
    if pd.notna(informacoes_comp) and informacoes_comp:
        contexto_servico += f"Mais Informações: {informacoes_comp}\n"
    if pd.notna(prazo) and prazo:
        contexto_servico += f"Prazo Esperado: {prazo}\n"
    if custo is not None and pd.notna(custo) and str(custo).strip(): # Checa se não é NaN e não é string vazia
        contexto_servico += f"Custo do Serviço: {custo}\n"

    prompt = f"""Você é um assistente da prefeitura do Rio de Janeiro.
Sua tarefa é responder à pergunta do cidadão de forma clara, concisa, amigável e útil, utilizando APENAS as informações fornecidas sobre o serviço abaixo.
Não invente informações, URLs ou detalhes que não estejam explicitamente no contexto fornecido.
A informação que você quer pode não estar explícita, mas deve ser inferida a partir dos dados do serviço.
Evite frases como "Com base nas informações fornecidas". Apenas use as informações.
Caso você indique que o usuário consulte um site, procure enviar a URL do site, se disponível no contexto fornecido.
Seja direto e responda à pergunta. Use marcadores (bullet points) se ajudar na clareza da resposta.

Contexto do Serviço:
{contexto_servico}

Pergunta do Cidadão: {question_text}

Resposta Ideal:
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao chamar Gemini para a pergunta '{question_text}' no serviço '{titulo}': {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar a resposta."

def process_row_for_responses(row):
    """
    Processa uma linha do DataFrame, pega as perguntas geradas (lidas do CSV como string)
    e cria respostas ideais para cada uma. Retorna uma lista de respostas.
    """
    try:
        perguntas_str = row['perguntas_geradas']
        if pd.isna(perguntas_str):
            return []

        perguntas_list = ast.literal_eval(perguntas_str)
        if not isinstance(perguntas_list, list):
            print(f"Aviso: 'perguntas_geradas' para '{row.get('titulo', 'N/A')}' não é uma lista após eval. Conteúdo: {perguntas_list}")
            return ["Erro: formato de perguntas inválido"] * (len(perguntas_list) if hasattr(perguntas_list, '__len__') else 1)

    except (ValueError, SyntaxError) as e:
        print(f"Erro ao parsear 'perguntas_geradas' para '{row.get('titulo', 'N/A')}': {e}. Conteúdo: {row['perguntas_geradas']}")
        return ["Erro ao ler a lista de perguntas"]
    except Exception as e:
        print(f"Erro inesperado ao processar perguntas para '{row.get('titulo', 'N/A')}': {e}")
        return ["Erro inesperado"]


    ideal_responses = []
    for pergunta in perguntas_list:
        if isinstance(pergunta, str) and pergunta.strip():
            # Passa o 'row' inteiro para que generate_ideal_response possa acessar todos os campos
            resposta = generate_ideal_response(row, pergunta)
            ideal_responses.append(resposta)
        else:
            ideal_responses.append("Pergunta inválida ou vazia, resposta não gerada.")
    return ideal_responses

# Nomes das coleções
collections_names = ["1746", "carioca-digital"]

for collection_name in collections_names:
    input_csv_path = f"perguntas_baseadas_no_{collection_name}.csv"
    output_exploded_csv_path = f"servicos_perguntas_respostas_{collection_name}.csv"

    print(f"\nProcessando arquivo: {input_csv_path}...")

    if not os.path.exists(input_csv_path):
        print(f"Arquivo {input_csv_path} não encontrado. Pulando...")
        continue

    try:
        df = pd.read_csv(input_csv_path, encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler o arquivo {input_csv_path}: {e}. Pulando...")
        continue

    if 'perguntas_geradas' not in df.columns:
        print(f"Coluna 'perguntas_geradas' não encontrada em {input_csv_path}. Pulando...")
        continue

    # Etapa 1: Gerar as listas de respostas para cada serviço
    print(f"Gerando respostas ideais para {collection_name}...")



############################
    # Seleciona 10 linhas aleatórias do DataFrame para depuração
    df_sample = df.sample(n=100, random_state=42)  # Para depuração, se necessário
    df = df_sample
############################



    # A função 'process_row_for_responses' retorna uma lista de strings (respostas)
    df['lista_respostas_ideais'] = df.progress_apply(process_row_for_responses, axis=1)

    # Etapa 2: Explodir o DataFrame
    print(f"Explodindo o DataFrame para {collection_name}...")
    expanded_data_list = []
    
    # Colunas a serem mantidas e replicadas em cada linha explodida
    # Excluímos as colunas que contêm as listas que serão explodidas
    columns_to_replicate = [col for col in df.columns if col not in ['perguntas_geradas', 'lista_respostas_ideais']]

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Explodindo {collection_name}"):
        try:
            perguntas_str = row['perguntas_geradas']
            if pd.isna(perguntas_str):
                perguntas_list = []
            else:
                perguntas_list = ast.literal_eval(perguntas_str)
                if not isinstance(perguntas_list, list): # Checagem extra
                    print(f"Aviso: 'perguntas_geradas' na linha {index} não resultou em lista. Conteúdo: {perguntas_list}")
                    perguntas_list = []
        except (ValueError, SyntaxError) as e:
            print(f"Aviso: Falha ao parsear 'perguntas_geradas' na linha {index} para '{row.get('titulo', 'N/A')}': {e}. Pulando perguntas desta linha.")
            perguntas_list = []

        respostas_list = row['lista_respostas_ideais'] # Já é uma lista Python
        if not isinstance(respostas_list, list): # Segurança
             print(f"Aviso: 'lista_respostas_ideais' na linha {index} não é uma lista. Conteúdo: {respostas_list}")
             respostas_list = []


        # Garantir que iteramos pelo número correto de pares pergunta/resposta
        num_pares = min(len(perguntas_list), len(respostas_list))
        if len(perguntas_list) != len(respostas_list):
            print(f"Aviso: Número de perguntas ({len(perguntas_list)}) e respostas ({len(respostas_list)}) difere para o serviço '{row.get('titulo', 'N/A')}' (linha {index}). Usando {num_pares} pares.")

        for i in range(num_pares):
            new_expanded_row = {}
            # Copiar os dados originais do serviço
            for col_name in columns_to_replicate:
                new_expanded_row[col_name] = row[col_name]
            
            # Adicionar a pergunta e resposta específicas desta linha explodida
            new_expanded_row['pergunta_individual'] = perguntas_list[i]
            new_expanded_row['resposta_ideal_individual'] = respostas_list[i]
            
            expanded_data_list.append(new_expanded_row)

    if not expanded_data_list:
        print(f"Nenhuma linha foi gerada após a explosão para {collection_name}. Verifique os dados e logs.")
        continue
        
    df_exploded = pd.DataFrame(expanded_data_list)

    # Salvar o DataFrame explodido
    try:
        df_exploded.to_csv(output_exploded_csv_path, index=False, encoding="utf-8")
        print(f"Arquivo explodido salvo em: {output_exploded_csv_path}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo explodido {output_exploded_csv_path}: {e}")

print("\nProcessamento e explosão concluídos para todos os arquivos.")

######
# Checando o CSV explodido
#####

import pandas as pd

# Lendo os 2 collection CSVs explodidos para análise 
# e unindo-os em um único DataFrame
df_1746 = pd.read_csv("servicos_perguntas_respostas_1746.csv", encoding="utf-8")
df_carioca_digital = pd.read_csv("servicos_perguntas_respostas_carioca-digital.csv", encoding="utf-8")
df_exploded = pd.concat([df_1746, df_carioca_digital], ignore_index=True)

# Salvando o DataFrame combinado em um único CSV
df_exploded.to_csv("servicos_perguntas_respostas.csv", index=False, encoding="utf-8")

# # Lendo o CSV explodido para análise
# df_exploded = pd.read_csv("typesense-client/servicos_perguntas_respostas_1746.csv", encoding="utf-8")
# print(df_exploded.head(10))

# # mostre as primeiras 10 perguntas e respostas
# for index, row in df_exploded.head(10).iterrows():
#     print(f"Pergunta: {row['pergunta_individual']}")
#     print(f"Resposta Ideal: {row['resposta_ideal_individual']}")
#     print("-" * 40)