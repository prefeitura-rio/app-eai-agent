import os
import sys
from datetime import datetime

import pandas as pd
import phoenix as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from src.config import env

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)
DATASET_PATH = "src/evaluations/letta/phoenix/training_dataset/dataset_treino_GPT.csv"
training_dataset = pd.read_csv(DATASET_PATH, encoding="utf-8")

keeping_columns = [
    "pergunta_individual",
    # "resposta_ideal_individual",
    "titulo",
    "descricao",
    "informacoes_complementares",
    "prazo_esperado",
    "resumo_whatsapp",
    "orgao_gestor",
]

training_dataset = (
    training_dataset[keeping_columns]
    .dropna(subset=["pergunta_individual"])#, "resposta_ideal_individual"])
    .rename(
        columns={
            "pergunta_individual": "pergunta",
            #"resposta_ideal_individual": "resposta_ideal",
        }
    )
)

now = datetime.now().strftime("%Y-%m-%d")
dataset_name = f"GPT_Dataset-{now}"

dataset = phoenix_client.upload_dataset(
    dataframe=training_dataset.head(50), 
    dataset_name=dataset_name, 
    input_keys=[
        "pergunta",
        "titulo",
        "descricao",
        "informacoes_complementares",
        "prazo_esperado",
        "resumo_whatsapp",
        "orgao_gestor",
    ], 
    #output_keys=["resposta_ideal"],
)

print(f"Dataset '{dataset_name}' enviado com sucesso para o Phoenix!")
