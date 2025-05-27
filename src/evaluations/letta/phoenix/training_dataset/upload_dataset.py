import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from src.config import env
from datetime import datetime
import pandas as pd
import phoenix as px

api_key = env.GEMINI_API_KEY

phoenix_client = px.Client(endpoint="http://34.60.92.205:6006")

training_dataset = pd.read_csv("src/evaluations/letta/phoenix/training_dataset/servicos_perguntas_respostas.csv", encoding="utf-8")

keeping_columns = [
    "pergunta_individual",
    "resposta_ideal_individual",
    "titulo",
    "descricao",
    "informacoes_complementares",
    "prazo_esperado",
    "resumo_whatsapp",
    "orgao_gestor",
]

training_dataset = training_dataset[keeping_columns]
training_dataset = training_dataset.dropna(subset=["pergunta_individual", "resposta_ideal_individual"])

# Rename columns pergunta_individual and resposta_ideal_invidividual
training_dataset = training_dataset.rename(
    columns={
        "pergunta_individual": "pergunta",
        "resposta_ideal_individual": "resposta_ideal",
    }
)

now = datetime.now().strftime("%Y-%m-%d")
# create a dataset consisting of input questions and expected outputs
dataset = phoenix_client.upload_dataset(dataframe=training_dataset, 
                                   dataset_name=f"Typesense_IA_Dataset-{now}", 
                                   input_keys=["pergunta", "titulo", "descricao", "informacoes_complementares", "prazo_esperado", "resumo_whatsapp", "orgao_gestor"], 
                                   output_keys=["resposta_ideal"])