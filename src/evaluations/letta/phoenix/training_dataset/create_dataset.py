import os
import csv
import ast
import requests
import typesense
import pandas as pd
from tqdm import tqdm
import google.generativeai as genai

from src.config import env

tqdm.pandas()

TYPESENSE_API_KEY = env.TYPESENSE_API_KEY
GEMINI_API_KEY = env.GEMINI_API_KEY

client = typesense.Client({
    "nodes": [{
        "host": "staging.typesense.dados.rio",
        "port": "443", # "8108",
        "protocol": "https"
    }],
    "api_key": TYPESENSE_API_KEY,
    "connection_timeout_seconds": 15
})

try:
    r = requests.get("https://staging.typesense.dados.rio:443/health", timeout=10)
    print(r.text)
except Exception as e:
    print(e)

genai.configure(api_key=GEMINI_API_KEY)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    safety_settings=safety_settings,
    generation_config=generation_config
)


def export_collections_to_csv(collection_name):
    query_params = {
        "q": "*",
        "query_by": "titulo",
        "per_page": 250,
        "page": 1
    }

    all_docs = []

    while True:
        response = client.collections[collection_name].documents.search(query_params)
        hits = response['hits']

        if not hits:
            break

        for hit in hits:
            all_docs.append(hit['document'])

        query_params["page"] += 1

    print(f"[{collection_name}] Total de documentos exportados: {len(all_docs)}")

    fieldnames = sorted({key for doc in all_docs for key in doc.keys()})
    filename = f"exported_typesense_{collection_name}_data.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_docs)
    
    print(f"[{collection_name}] CSV salvo como {filename}")



def generate_questions(row):
    prompt = f"""Gere 5 perguntas que um cidadão poderia fazer sobre o serviço da prefeitura descrito abaixo. Retorne apenas as perguntas em uma lista sem numeração e uma por linha.
    
Título: {row['titulo']}
Descrição: {row.get('descricao_texto_normalizado', '')}
Informações complementares: {row.get('informacoes_complementares', '')}
Prazo: {row.get('prazo_esperado', '')}
Custo: {row.get('custo_do_servico', '')}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip().split("\n")[:5]
    except:
        print(f"Erro ao gerar perguntas para '{row.get('titulo')}': {e}")
        return []


def generate_ideal_response(row_data, question_text):
    contexto = f"""Título: {row_data.get('titulo', 'N/A')}
Descrição: {row_data.get('descricao_texto_normalizado', 'N/A')}
Informações complementares: {row_data.get('informacoes_complementares', 'N/A')}
Prazo esperado: {row_data.get('prazo_esperado', 'N/A')}
Custo: {row_data.get('custo_do_servico') or row_data.get('custo') or 'N/A'}
"""

    prompt = f"""Você é um assistente da prefeitura do Rio de Janeiro.
Sua tarefa é responder à pergunta do cidadão de forma clara, concisa, amigável e baseada APENAS no contexto fornecido.
Não invente informações, URLs ou detalhes que não estejam explicitamente no contexto fornecido.
A informação que você quer pode não estar explícita, mas deve ser inferida a partir dos dados do serviço.
Evite frases como "Com base nas informações fornecidas". Apenas use as informações.
Caso você indique que o usuário consulte um site, procure enviar a URL do site, se disponível no contexto fornecido.
Seja direto e responda à pergunta. Use marcadores (bullet points) se ajudar na clareza da resposta.

Contexto do Serviço:
{contexto}

Pergunta do Cidadão: {question_text}

Resposta:
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao gerar resposta para '{question_text}': {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar a resposta."


def process_row_for_responses(row):
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
            resposta = generate_ideal_response(row, pergunta)
            ideal_responses.append(resposta)
        else:
            ideal_responses.append("Pergunta inválida ou vazia, resposta não gerada.")
    
    return ideal_responses


def explode_dataframe(df, collection_name):
    expanded_data_list = []

    columns_to_replicate = [
        col for col in df.columns if col not in ['perguntas_geradas', 'lista_respostas_ideais']
    ]

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Explodindo {collection_name}"):
        try:
            perguntas_str = row["perguntas_geradas"]
            perguntas_list = ast.literal_eval(perguntas_str) if pd.notna(perguntas_str) else []
            if not isinstance(perguntas_list, list):
                print(f"Aviso: 'perguntas_geradas' na linha {index} não resultou em lista. Conteúdo: {perguntas_list}")
                perguntas_list = []
        except (ValueError, SyntaxError) as e:
            print(f"Aviso: Falha ao parsear 'perguntas_geradas' na linha {index} ('{row.get('titulo', 'N/A')}'): {e}.")
            perguntas_list = []

        
        try:
            respostas_str = row['lista_respostas_ideais']
            respostas_list = ast.literal_eval(respostas_str) if pd.notna(respostas_str) else []
            if not isinstance(respostas_list, list):
                print(f"Aviso: 'lista_respostas_ideais' na linha {index} não é uma lista. Conteúdo: {respostas_list}")
                respostas_list = []
        except (ValueError, SyntaxError):
            print(f"Aviso: Falha ao parsear 'lista_respostas_ideais' na linha {index}.")
            respostas_list = []

        num_pares = min(len(perguntas_list), len(respostas_list))
        if len(perguntas_list) != len(respostas_list):
            print(f"Aviso: Número de perguntas ({len(perguntas_list)}) e respostas ({len(respostas_list)}) difere para o serviço '{row.get('titulo', 'N/A')}' (linha {index}). Usando {num_pares} pares.")

        for i in range(num_pares):
            new_expanded_row = {}
            for col_name in columns_to_replicate:
                new_expanded_row[col_name] = row[col_name]
            
            new_expanded_row['pergunta_individual'] = perguntas_list[i]
            new_expanded_row['resposta_ideal_individual'] = respostas_list[i]
            
            expanded_data_list.append(new_expanded_row)
        
    if not expanded_data_list:
        print(f"Nenhuma linha foi gerada após a explosão para {collection_name}. Verifique os dados e logs.")
        return pd.DataFrame()
    
    return pd.DataFrame(expanded_data_list)


def process_collection(collection_name):
    input_csv = f"perguntas_baseadas_no_{collection_name}.csv"
    output_csv = f"servicos_perguntas_respostas_{collection_name}.csv"

    print(f"\nProcessando arquivo: {input_csv}...")

    if not os.path.exists(input_csv):
        print(f"Arquivo {input_csv} não encontrado. Pulando...")
        return

    try:
        df = pd.read_csv(input_csv, encoding="utf-8")
    except Exception as e:
        print(f"Erro ao ler o arquivo {input_csv}: {e}. Pulando...")
        return

    if 'perguntas_geradas' not in df.columns:
        print(f"Coluna 'perguntas_geradas' não encontrada em {input_csv}. Pulando...")
        return

    print(f"Gerando respostas ideais para {collection_name}...")
    df['lista_respostas_ideais'] = df.progress_apply(process_row_for_responses, axis=1)

    df_exploded = explode_dataframe(df, collection_name)

    if df_exploded.empty:
        print(f"Nenhuma linha explodida para {collection_name}.")
        return

    try:
        df_exploded.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"Arquivo salvo: {output_csv}")
    except Exception as e:
        print(f"Erro ao salvar {output_csv}: {e}")


def merge_collections():
    files = ["servicos_perguntas_respostas_1746_2.csv", "servicos_perguntas_respostas_carioca-digital_2.csv"]
    dfs = []

    for file in files:
        if os.path.exists(file):
            dfs.append(pd.read_csv(file, encoding="utf-8"))
        else:
            print(f"Arquivo {file} não encontrado.")

    if dfs:
        df_merged = pd.concat(dfs, ignore_index=True)
        df_merged.to_csv("servico_perguntas_respostas.csv", index=False, encoding="utf-8")
        print("Arquivo salvo como 'servicos_perguntas_respostas.csv'")


def generate_questions_csv(collection_name):
    # export_collections_to_csv(collection)

    drop_columns = ["embedding", "link_acesso", "ultima_atualizacao", "url", "tipo", "id_carioca_digital"] if collection_name == "carioca-digital" else ["embedding", "ultima_atualizacao", "url", "tipo"]
    df = pd.read_csv(f"exported_typesense_{collection_name}_data.csv", encoding="utf-8").drop(columns=drop_columns)
    df["perguntas_geradas"] = df.progress_apply(generate_questions, axis=1)
    df.to_csv(f"perguntas_baseadas_no_{collection_name}.csv", index=False)


if __name__ == "__main__":
    collections = ["carioca-digital", "1746"]

    for collection in collections:
        # generate_questions_csv(collection)
        process_collection(collection)

    merge_collections()
