"""
Schemas Pydantic para definir contratos de API claros e validação de dados.
"""

from pydantic import BaseModel


class ExperimentData(BaseModel):
    """Dados completos do experimento."""

    dataset_id: str
    experiment_id: str
    dataset_name: str
    experiment_name: str
    experiment_metadata: dict
    experiment: list

    class Config:
        extra = "ignore"
