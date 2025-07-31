# src/api/v1/experiments.py
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from src.core.security.dependencies import validar_token

from src.utils.bigquery import get_bigquery_result
from google.cloud.exceptions import GoogleCloudError
from src.utils.log import logger

# router = APIRouter(dependencies=[Depends(validar_token)], tags=["Experiments"])
router = APIRouter(tags=["Experiments"])

# --- Pydantic Response Models ---

DATASET_TABLE = "rj-iplanrio.brutos_eai_logs.evaluations_datasets"
EXPERIMENTS_TABLE = "rj-iplanrio.brutos_eai_logs.evaluations_experiments"


class DatasetInfo(BaseModel):
    dataset_id: str
    dataset_name: str
    dataset_description: str
    num_examples: int = Field(..., description="Number of examples in the dataset.")
    num_runs: int = Field(
        ..., description="Number of experiments run against this dataset."
    )
    created_at: datetime


class DatasetExperimentInfo(BaseModel):
    dataset_id: str
    experiment_id: str
    experiment_name: str
    experiment_description: str
    experiment_timestamp: datetime
    execution_summary: Dict[str, Any]
    error_summary: Dict[str, Any]
    aggregate_metrics: List[Dict[str, Any]]


class DatasetExamplesInfo(BaseModel):
    dataset_id: str
    num_examples: int = Field(..., description="Number of examples in the dataset.")
    examples: List[Dict[str, Any]]


class ExperimentDetails(BaseModel):
    dataset_id: str
    dataset_name: str
    dataset_description: str
    experiment_id: str
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
    query = f"""
        SELECT
            CAST(d.dataset_id AS STRING) AS dataset_id,
            d.dataset_name,
            d.dataset_description,
            d.created_at,
            COALESCE(ARRAY_LENGTH(JSON_EXTRACT_ARRAY(d.data)), 0) AS num_examples,
            COALESCE(e.num_runs, 0) as num_runs
        FROM
            `{DATASET_TABLE}` AS d
        LEFT JOIN (
            SELECT
                dataset_id,
                COUNT(experiment_id) as num_runs
            FROM
                `{EXPERIMENTS_TABLE}`
            GROUP BY
                dataset_id
        ) AS e
        ON d.dataset_id = e.dataset_id
        ORDER BY
            d.dataset_name;
    """

    logger.info("Executing query to fetch all datasets summary.")
    try:
        results = get_bigquery_result(query)
        return results
    except GoogleCloudError as e:
        logger.error(f"BigQuery error fetching datasets: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )


@router.get("/dataset_experiments", response_model=List[DatasetExperimentInfo])
async def get_dataset_experiments(
    dataset_id: str = Query(
        ..., description="The ID of the dataset to retrieve experiments for."
    )
):
    """
    Returns a list of all experiments associated with a specific dataset ID.
    """
    query = f"""
        SELECT
            CAST(e.dataset_id AS STRING) AS dataset_id,
            CAST(e.experiment_id AS STRING) AS experiment_id,
            e.experiment_name,
            e.experiment_description,
            e.experiment_timestamp,
            execution_summary,
            e.error_summary,
            e.aggregate_metrics
        FROM `{EXPERIMENTS_TABLE}` e
        WHERE e.dataset_id = CAST({dataset_id} AS INT64)
        ORDER BY e.experiment_timestamp DESC;
    """
    logger.info(f"Executing query for experiments with dataset_id: {dataset_id}")
    try:
        results = get_bigquery_result(query)
        return results
    except GoogleCloudError as e:
        logger.error(
            f"BigQuery error fetching experiments for dataset {dataset_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )


@router.get("/dataset_examples", response_model=List[DatasetExamplesInfo])
async def get_dataset_examples(
    dataset_id: str = Query(
        ..., description="The ID of the dataset to retrieve experiments for."
    )
):
    """
    Returns a list of all available datasets with a summary of each.
    """
    query = f"""
        SELECT
            CAST(d.dataset_id AS STRING) AS dataset_id,
            COALESCE(ARRAY_LENGTH(JSON_EXTRACT_ARRAY(d.data)), 0) AS num_examples,
            d.data as examples,
        FROM `{DATASET_TABLE}` AS d
        WHERE d.dataset_id = CAST({dataset_id} AS INT64)
    """

    logger.info("Executing query to fetch all datasets summary.")
    try:
        results = get_bigquery_result(query)
        return results
    except GoogleCloudError as e:
        logger.error(f"BigQuery error fetching datasets: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )


@router.get("/experiments", response_model=ExperimentDetails)
async def get_experiment_details(
    dataset_id: str = Query(..., description="The ID of the dataset."),
    experiment_id: str = Query(
        ..., description="The ID of the experiment to retrieve."
    ),
):
    """
    Returns all data for a single, specific experiment.
    """
    query = f"""
        SELECT 
            dataset_name,
            dataset_description,
            CAST(dataset_id AS STRING) AS dataset_id,
            CAST(experiment_id AS STRING) AS experiment_id,
            experiment_name,
            experiment_description,
            experiment_timestamp,
            experiment_metadata,
            execution_summary,
            error_summary,
            aggregate_metrics,
            runs
        FROM `{EXPERIMENTS_TABLE}` 
        WHERE dataset_id = CAST({dataset_id} AS INT64) AND experiment_id = CAST({experiment_id} AS INT64) LIMIT 1;
    """

    logger.info(
        f"Executing query for experiment_id: {experiment_id} and dataset_id: {dataset_id}"
    )
    try:
        results = get_bigquery_result(query)
        if not results:
            raise HTTPException(status_code=404, detail="Experiment not found.")
        return dict(results[0])
    except GoogleCloudError as e:
        logger.error(f"BigQuery error fetching experiment {experiment_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from BigQuery."
        )
