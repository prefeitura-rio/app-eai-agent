import pandas as pd
import phoenix as px

from src.config import env

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)


def upload_dataset(dataset_name: str, dataframe: pd.DataFrame):
    dataset = phoenix_client.upload_dataset(
        dataframe=dataframe,
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
        # output_keys=["resposta_ideal"],
    )

    print(f"Dataset '{dataset_name}' enviado com sucesso para o Phoenix!")


def main():

    url = "https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785"
    url = url.replace("/edit?gid=", "/export?format=csv&gid=")
    print(url)
    dataframe = pd.read_csv(
        url,
        encoding="utf-8",
    )

    print(dataframe.columns)
    print(dataframe.head())

    # upload_dataset(dataset_name=dataset_name, dataframe=dataframe)


if __name__ == "__main__":
    main()
