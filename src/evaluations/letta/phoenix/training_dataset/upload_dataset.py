import pandas as pd
import phoenix as px

from src.config import env

phoenix_client = px.Client(endpoint=env.PHOENIX_ENDPOINT)


def upload_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
    input_keys: list,
    output_keys: list,
    metadata_keys: list,
    dataset_description: str,
):
    dataset = phoenix_client.upload_dataset(
        dataframe=dataframe,
        dataset_name=dataset_name,
        input_keys=input_keys,
        output_keys=output_keys,
        metadata_keys=metadata_keys,
        dataset_description=dataset_description,
    )

    print(f"Dataset '{dataset_name}' enviado com sucesso para o Phoenix!\n\n")


def main():

    url = "https://docs.google.com/spreadsheets/d/1VPnJSf9puDgZ-Ed9MRkpe3Jy38nKxGLp7O9-ydAdm98/edit?gid=370781785"
    url = url.replace("/edit?gid=", "/export?format=csv&gid=")
    print(url)
    dataframe = pd.read_csv(
        url,
        encoding="utf-8",
    )

    input_keys = ["mensagem_whatsapp_simulada"]
    output_keys = ["golden_answer"]
    metadata_keys = [
        "id",
        "tema",
        "subtema",
        "golden_links_list",
    ]

    datasets_to_upload = [
        # {
        #     "dataset_name": "golden_dataset_v5",
        #     "dataframe": dataframe,
        #     "input_keys": input_keys,
        #     "output_keys": output_keys,
        #     "metadata_keys": metadata_keys,
        #     "dataset_description": "Golden Dataset - 241 samples",
        # },
        # {
        #     "dataset_name": "golden_dataset_v5_small_sample",
        #     "dataframe": dataframe.head(10),
        #     "input_keys": input_keys,
        #     "output_keys": output_keys,
        #     "metadata_keys": metadata_keys,
        #     "dataset_description": "Golden Dataset - 10 samples",
        # },
        {
            "dataset_name": "golden_dataset_v5_30_samples",
            "dataframe": dataframe.head(30),
            "input_keys": input_keys,
            "output_keys": output_keys,
            "metadata_keys": metadata_keys,
            "dataset_description": "Golden Dataset - 10 samples",
        },
        # {
        #     "dataset_name": "golden_dataset_v4_very_small_sample",
        #     "dataframe": dataframe.head(1),
        #     "input_keys": input_keys,
        #     "output_keys": output_keys,
        #     "metadata_keys": metadata_keys,
        #     "dataset_description": "Golden Dataset - 1 sample",
        # },
    ]

    print(dataframe)

    for dataset in datasets_to_upload:
        upload_dataset(
            dataset_name=dataset["dataset_name"],
            dataframe=dataset["dataframe"],
            input_keys=dataset["input_keys"],
            output_keys=dataset["output_keys"],
            metadata_keys=dataset["metadata_keys"],
            dataset_description=dataset["dataset_description"],
        )


if __name__ == "__main__":
    main()
