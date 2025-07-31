# src/api/v1/experiments.py
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from src.core.security.dependencies import validar_token

from src.utils.bigquery import get_bigquery_client
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from src.utils.log import logger

router = APIRouter(dependencies=[Depends(validar_token)], tags=["Experiments"])

# --- Pydantic Response Models ---


class DatasetInfo(BaseModel):
    dataset_id: int
    dataset_name: str
    dataset_description: str
    examples: int = Field(..., description="Number of examples in the dataset.")
    num_runs: int = Field(
        ..., description="Number of experiments run against this dataset."
    )


class DatasetExperimentInfo(BaseModel):
    dataset_id: int
    experiment_id: int
    experiment_name: str
    experiment_description: str
    experiment_timestamp: datetime
    error_summary: Dict[str, Any]
    aggregate_metrics: List[Dict[str, Any]]


class ExperimentDetails(BaseModel):
    dataset_id: int
    dataset_name: str
    dataset_description: str
    experiment_id: int
    experiment_name: str
    experiment_description: str
    experiment_timestamp: datetime
    experiment_metadata: Dict[str, Any]
    execution_summary: Dict[str, Any]
    error_summary: Dict[str, Any]
    aggregate_metrics: List[Dict[str, Any]]
    runs: List[Dict[str, Any]]


# --- API Endpoints ---


@router.get("/datasets", response_model=List[DatasetInfo])
async def get_all_datasets():
    """
    Returns a list of all available datasets with a summary of each.
    """
    client = get_bigquery_client()
    datasets_table = "rj-iplanrio.brutos_eai_logs.evaluations_datasets"
    experiments_table = "rj-iplanrio.brutos_eai_logs.evaluations_experiments"

    query = f"""
        SELECT
            d.dataset_id,
            d.dataset_name,
            d.dataset_description,
            JSON_ARRAY_LENGTH(d.data) as examples,
            COALESCE(e.num_runs, 0) as num_runs
        FROM
            `{datasets_table}` AS d
        LEFT JOIN (
            SELECT
                dataset_id,
                COUNT(experiment_id) as num_runs
            FROM
                `{experiments_table}`
            GROUP BY
                dataset_id
        ) AS e
        ON d.dataset_id = e.dataset_id
        ORDER BY
            d.dataset_name;
    """
    logger.info("Executing query to fetch all datasets summary.")
    try:
        query_job = client.query(query)
        results = [dict(row) for row in query_job.result()]
        return results
    except GoogleCloudError as e:
        logger.error(f"BigQuery error fetching datasets: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )


@router.get("/dataset_experiments", response_model=List[DatasetExperimentInfo])
async def get_dataset_experiments(
    dataset_id: int = Query(
        ..., description="The ID of the dataset to retrieve experiments for."
    )
):
    """
    Returns a list of all experiments associated with a specific dataset ID.
    """
    client = get_bigquery_client()
    table = "rj-iplanrio.brutos_eai_logs.evaluations_experiments"
    query = f"""
        SELECT
            dataset_id,
            experiment_id,
            experiment_name,
            experiment_description,
            experiment_timestamp,
            error_summary,
            aggregate_metrics
        FROM `{table}`
        WHERE dataset_id = @dataset_id
        ORDER BY experiment_timestamp DESC;
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_id", "INT64", dataset_id)
        ]
    )
    logger.info(f"Executing query for experiments with dataset_id: {dataset_id}")
    try:
        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job.result()]
        return results
    except GoogleCloudError as e:
        logger.error(
            f"BigQuery error fetching experiments for dataset {dataset_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )


@router.get("/experiments", response_model=ExperimentDetails)
async def get_experiment_details(
    dataset_id: int = Query(..., description="The ID of the dataset."),
    experiment_id: int = Query(
        ..., description="The ID of the experiment to retrieve."
    ),
):
    """
    Returns all data for a single, specific experiment.
    """
    client = get_bigquery_client()
    table = "rj-iplanrio.brutos_eai_logs.evaluations_experiments"
    query = f"SELECT * FROM `{table}` WHERE dataset_id = @dataset_id AND experiment_id = @experiment_id LIMIT 1;"

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_id", "INT64", dataset_id),
            bigquery.ScalarQueryParameter("experiment_id", "INT64", experiment_id),
        ]
    )
    logger.info(
        f"Executing query for experiment_id: {experiment_id} and dataset_id: {dataset_id}"
    )
    try:
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        if not results:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        return dict(results[0])
    except GoogleCloudError as e:
        logger.error(f"BigQuery error fetching experiment {experiment_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )
