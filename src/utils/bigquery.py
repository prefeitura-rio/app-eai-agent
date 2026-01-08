from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Dict, Any
import base64
import json
import src.config.env as env
import datetime
import pytz
from src.utils.log import logger
from google.cloud.exceptions import GoogleCloudError
from src.config import env
from google.cloud.bigquery.table import Row
import numpy as np
import pandas as pd


class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder customizado que sabe como converter objetos
    de data, hora e data/hora do Python para strings no padrão ISO 8601.
    """

    def default(self, obj):
        # Se o objeto for uma instância de datetime, date ou time...
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            # ... converta-o para uma string no formato ISO.
            return obj.isoformat()

        # Para qualquer outro tipo, deixe o encoder padrão fazer o trabalho.
        return super().default(obj)


def get_bigquery_result(query: str):
    bq_client = get_bigquery_client()
    query_job = bq_client.query(query)
    result = query_job.result(page_size=env.GOOGLE_BIGQUERY_PAGE_SIZE)
    data = []
    for page in result.pages:
        for row in page:
            row: Row
            row_data = dict(row.items())
            data.append(row_data)

    data_str = json.dumps(data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False)

    return json.loads(data_str)


def get_bigquery_client() -> bigquery.Client:
    """Get the BigQuery client.

    Returns:
        bigquery.Client: The BigQuery client.
    """
    credentials = get_gcp_credentials(
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    )
    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def get_gcp_credentials(scopes: List[str] = None) -> service_account.Credentials:
    """Get the GCP credentials.

    Args:
        scopes (List[str], optional): The scopes to use. Defaults to None.

    Returns:
        service_account.Credentials: The GCP credentials.
    """
    info: dict = json.loads(base64.b64decode(env.GCP_SERVICE_ACCOUNT_CREDENTIALS))
    creds = service_account.Credentials.from_service_account_info(info)
    if scopes:
        creds = creds.with_scopes(scopes)
    return creds


def get_datetime() -> str:
    timestamp = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")


def save_response_in_bq(
    data: dict,
    endpoint: str,
    dataset_id: str,
    table_id: str,
    project_id: str = "rj-iplanrio",
):
    table_full_name = f"{project_id}.{dataset_id}.{table_id}"
    logger.info(f"Salvando resposta no BigQuery: {table_full_name}")
    schema = [
        bigquery.SchemaField("datetime", "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("endpoint", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("data", "JSON", mode="NULLABLE"),
        bigquery.SchemaField("data_particao", "DATE", mode="NULLABLE"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_APPEND",
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="data_particao",  # name of column to use for partitioning
        ),
    )
    datetime_to_save = get_datetime()
    data_to_save = {
        "datetime": datetime_to_save,
        "endpoint": endpoint,
        "data": data,
        "data_particao": datetime_to_save.split("T")[0],
    }
    json_data = json.loads(json.dumps([data_to_save]))
    client = get_bigquery_client()

    try:
        job = client.load_table_from_json(
            json_data, table_full_name, job_config=job_config
        )
        job.result()
        logger.info(f"Resposta salva no BigQuery: {table_full_name}")
    except Exception:
        raise Exception(json_data)


def clean_json_field(obj):
    """
    Limpa campos JSON recursivamente: converte NaN para None,
    converte numpy/pandas types e força serialização válida.
    """
    if isinstance(obj, float) and np.isnan(obj):
        return None
    elif isinstance(obj, (np.generic, pd.Timestamp)):
        return obj.item() if hasattr(obj, "item") else str(obj)
    elif isinstance(obj, dict):
        return {k: clean_json_field(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_field(v) for v in obj]
    else:
        return obj


def upload_experiment_to_bq(result_data: Dict[str, Any]):
    """
    Faz o upload do resultado do experimento para a tabela de experiments no BigQuery,
    usando load_table_from_json para garantir a criação da tabela e o schema correto.
    """
    try:
        experiment_id = result_data["experiment_id"]
        logger.info(f"Fazendo upload do experimento {experiment_id} para o BigQuery...")
        client = get_bigquery_client()
        table_full_name = "rj-iplanrio.brutos_eai_logs.evaluations_experiments"

        json_data = [result_data]

        schema = [
            bigquery.SchemaField(
                "dataset_name",
                "STRING",
                mode="NULLABLE",
                description="Nome legível do dataset.",
            ),
            bigquery.SchemaField(
                "dataset_description",
                "STRING",
                mode="NULLABLE",
                description="Descrição do dataset.",
            ),
            bigquery.SchemaField(
                "dataset_id",
                "INTEGER",
                mode="REQUIRED",
                description="ID do dataset usado (chave de partição).",
            ),
            bigquery.SchemaField(
                "experiment_id",
                "INTEGER",
                mode="REQUIRED",
                description="ID único da execução do experimento.",
            ),
            bigquery.SchemaField(
                "experiment_name",
                "STRING",
                mode="NULLABLE",
                description="Nome do experimento.",
            ),
            bigquery.SchemaField(
                "experiment_description",
                "STRING",
                mode="NULLABLE",
                description="Descrição dos objetivos do experimento.",
            ),
            bigquery.SchemaField(
                "experiment_timestamp",
                "TIMESTAMP",
                mode="REQUIRED",
                description="Timestamp de conclusão do experimento.",
            ),
            bigquery.SchemaField(
                "experiment_metadata",
                "JSON",
                mode="NULLABLE",
                description="Metadados do experimento (config do agente, prompts).",
            ),
            bigquery.SchemaField(
                "execution_summary",
                "JSON",
                mode="NULLABLE",
                description="Resumo dos tempos de execução.",
            ),
            bigquery.SchemaField(
                "error_summary",
                "JSON",
                mode="NULLABLE",
                description="Resumo de erros e falhas.",
            ),
            bigquery.SchemaField(
                "aggregate_metrics",
                "JSON",
                mode="NULLABLE",
                description="Métricas agregadas de performance.",
            ),
            bigquery.SchemaField(
                "runs",
                "JSON",
                mode="NULLABLE",
                description="Resultados detalhados de cada tarefa (run).",
            ),
        ]

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition="WRITE_APPEND",
            range_partitioning=bigquery.RangePartitioning(
                field="dataset_id",
                range_=bigquery.PartitionRange(start=0, end=100000000, interval=10000),
            ),
        )

        json_fields = [
            "experiment_metadata",
            "execution_summary",
            "error_summary",
            "aggregate_metrics",
            "runs",
        ]

        for field in json_fields:
            if field in result_data:
                result_data[field] = clean_json_field(result_data[field])

        json_data = [result_data]

        job = client.load_table_from_json(
            json_data, table_full_name, job_config=job_config
        )
        job.result()

        logger.info(f"Experimento {experiment_id} salvo com sucesso no BigQuery.")

    except GoogleCloudError as e:
        logger.error(f"Falha na comunicação com o BigQuery: {e}")
    except Exception as e:
        logger.error(
            f"Erro inesperado durante o upload do experimento para o BigQuery: {e}"
        )


def upload_dataset_to_bq(dataset_config, filtered_df):
    """
    Faz o upload do dataset para a tabela de datasets no BigQuery se ele não existir.
    Apenas as colunas essenciais são enviadas.
    """
    try:
        client = get_bigquery_client()
        dataset_id = dataset_config["dataset_id"]
        table_full_name = "rj-iplanrio.brutos_eai_logs.evaluations_datasets"

        try:
            query = f"SELECT dataset_id FROM `{table_full_name}` WHERE dataset_id = @id LIMIT 1"
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("id", "INT64", dataset_id)
                ]
            )
            query_job = client.query(query, job_config=job_config)
            if list(query_job.result()):
                logger.info(
                    f"Dataset {dataset_id} já existe no BigQuery. Upload ignorado."
                )
                return
        except GoogleCloudError as e:
            if "Not found" in str(e):
                logger.info(f"Tabela {table_full_name} não encontrada. Criando...")
            else:
                raise

        logger.info(
            f"Fazendo upload do novo dataset {dataset_id} para o {table_full_name}..."
        )

        def sanitize_for_bigquery(df: pd.DataFrame) -> pd.DataFrame:
            def clean_value(x):
                if pd.isna(x):
                    return None
                if isinstance(x, (np.integer, np.floating, np.bool_)):
                    return x.item()
                return x

            return df.map(clean_value)

        filtered_df = sanitize_for_bigquery(filtered_df)

        row_to_insert = {
            "dataset_id": dataset_id,
            "dataset_name": dataset_config["dataset_name"],
            "dataset_description": dataset_config["dataset_description"],
            "created_at": dataset_config["dataset_created_at"],
            "data": filtered_df.to_dict(orient="records"),
        }

        schema = [
            bigquery.SchemaField(
                "dataset_id",
                "INTEGER",
                mode="REQUIRED",
                description="ID determinístico do dataset baseado em hash.",
            ),
            bigquery.SchemaField(
                "dataset_name",
                "STRING",
                mode="NULLABLE",
                description="Nome legível do dataset.",
            ),
            bigquery.SchemaField(
                "dataset_description",
                "STRING",
                mode="NULLABLE",
                description="Descrição do propósito do dataset.",
            ),
            bigquery.SchemaField(
                "created_at",
                "TIMESTAMP",
                mode="REQUIRED",
                description="Timestamp da criação do registro (campo de partição).",
            ),
            bigquery.SchemaField(
                "data",
                "JSON",
                mode="NULLABLE",
                description="Conteúdo completo do dataset com as tarefas.",
            ),
        ]
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition="WRITE_APPEND",
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="created_at",  # name of column to use for partitioning
            ),
        )
        job = client.load_table_from_json(
            [row_to_insert], table_full_name, job_config=job_config
        )
        job.result()
        logger.info(f"Dataset {dataset_id} salvo com sucesso no BigQuery.")

    except GoogleCloudError as e:
        logger.error(f"Falha na comunicação com o BigQuery: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado durante o upload para o BigQuery: {e}")
