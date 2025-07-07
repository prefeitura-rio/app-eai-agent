"""
Schemas Pydantic para definir contratos de API claros e validação de dados.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class PageInfo(BaseModel):
    """Informações de paginação."""

    endCursor: Optional[str] = None
    hasNextPage: bool = False

    class Config:
        extra = "ignore"


class AnnotationSummary(BaseModel):
    """Resumo de anotação."""

    annotationName: str
    minScore: Optional[float] = None
    maxScore: Optional[float] = None
    meanScore: Optional[float] = None

    class Config:
        extra = "ignore"


class ExperimentAnnotationSummary(BaseModel):
    """Resumo de anotação de experimento."""

    annotationName: str
    minScore: Optional[float] = None
    maxScore: Optional[float] = None

    class Config:
        extra = "ignore"


class Project(BaseModel):
    """Projeto."""

    id: str

    class Config:
        extra = "ignore"


class Experiment(BaseModel):
    """Experimento."""

    id: str
    name: str
    sequenceNumber: int
    description: Optional[str] = None
    createdAt: datetime
    metadata: Optional[Dict[str, Any]] = None
    errorRate: Optional[float] = None
    runCount: int
    averageRunLatencyMs: Optional[float] = None
    project: Optional[Project] = None
    annotationSummaries: List[AnnotationSummary] = []

    class Config:
        extra = "ignore"  # Ignora campos extras como __typename


class ExperimentEdge(BaseModel):
    """Edge de experimento para paginação."""

    experiment: Experiment
    cursor: str
    node: Optional[Dict[str, Any]] = None  # Para o campo node com __typename

    class Config:
        extra = "ignore"


class ExperimentsConnection(BaseModel):
    """Conexão de experimentos."""

    edges: List[ExperimentEdge] = []
    pageInfo: PageInfo

    class Config:
        extra = "ignore"


class Dataset(BaseModel):
    """Dataset."""

    id: str
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    createdAt: datetime
    exampleCount: int
    experimentCount: int
    experimentAnnotationSummaries: List[ExperimentAnnotationSummary] = []
    experiments: Optional[ExperimentsConnection] = None

    class Config:
        extra = "ignore"  # Ignora campos extras como __typename


class DatasetEdge(BaseModel):
    """Edge de dataset para paginação."""

    node: Dataset
    cursor: str

    class Config:
        extra = "ignore"


class DatasetsConnection(BaseModel):
    """Conexão de datasets."""

    edges: List[DatasetEdge] = []
    pageInfo: PageInfo

    class Config:
        extra = "ignore"


class DatasetsData(BaseModel):
    """Dados dos datasets."""

    datasets: DatasetsConnection

    class Config:
        extra = "ignore"


class DatasetsResponse(BaseModel):
    """Resposta da API de datasets."""

    data: DatasetsData

    class Config:
        extra = "ignore"


class DatasetExperimentsData(BaseModel):
    """Dados dos experimentos de um dataset."""

    dataset: Dataset

    class Config:
        extra = "ignore"


class DatasetExperimentsResponse(BaseModel):
    """Resposta da API de experimentos de um dataset."""

    data: DatasetExperimentsData

    class Config:
        extra = "ignore"


class Example(BaseModel):
    """Exemplo de dataset."""

    id: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    createdAt: datetime

    class Config:
        extra = "ignore"


class ExampleEdge(BaseModel):
    """Edge de exemplo para paginação."""

    node: Example
    cursor: str

    class Config:
        extra = "ignore"


class ExamplesConnection(BaseModel):
    """Conexão de exemplos."""

    edges: List[ExampleEdge] = []
    pageInfo: PageInfo

    class Config:
        extra = "ignore"


class DatasetExamplesData(BaseModel):
    """Dados dos exemplos de um dataset."""

    dataset: Dataset

    class Config:
        extra = "ignore"


class DatasetExamplesResponse(BaseModel):
    """Resposta da API de exemplos de um dataset."""

    data: DatasetExamplesData

    class Config:
        extra = "ignore"


class ToolCall(BaseModel):
    """Chamada de ferramenta."""

    name: str
    arguments: Dict[str, Any] = {}

    class Config:
        extra = "ignore"


class ToolReturn(BaseModel):
    """Retorno de ferramenta."""

    text: str = ""
    sources: List[Dict[str, Any]] = []
    web_search_queries: Optional[List[str]] = None

    class Config:
        extra = "ignore"


class Message(BaseModel):
    """Mensagem genérica."""

    content: Optional[str] = None
    reasoning: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    tool_return: Optional[ToolReturn] = None
    name: Optional[str] = None
    message_type: Optional[str] = None

    class Config:
        extra = "ignore"


class OrderedMessage(BaseModel):
    """Mensagem ordenada."""

    type: str
    message: Message

    class Config:
        extra = "ignore"


class GroupedMessages(BaseModel):
    """Mensagens agrupadas."""

    assistant_messages: List[Message] = []

    class Config:
        extra = "ignore"


class AgentOutput(BaseModel):
    """Saída do agente."""

    grouped: GroupedMessages
    ordered: List[OrderedMessage] = []

    class Config:
        extra = "ignore"


class ExperimentMetadata(BaseModel):
    """Metadados do experimento."""

    total_runs: Optional[int] = None
    run_samples: Optional[int] = None

    class Config:
        extra = "ignore"


class ExperimentRunDetail(BaseModel):
    """Detalhes de uma execução de experimento."""

    example_id: str
    example_id_clean: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    reference_output: Optional[Dict[str, Any]] = None
    annotations: List[Dict[str, Any]] = []

    class Config:
        extra = "ignore"


class ExperimentData(BaseModel):
    """Dados completos do experimento."""

    dataset_id: str
    experiment_id: str
    dataset_name: str
    experiment_name: str
    experiment_metadata: ExperimentMetadata
    experiment: List[ExperimentRunDetail]

    class Config:
        extra = "ignore"


class ReasoningStep(BaseModel):
    """Passo de raciocínio."""

    step: int
    type: str
    content: Union[str, Dict[str, Any]]

    class Config:
        extra = "ignore"


class Metric(BaseModel):
    """Métrica de avaliação."""

    annotation_name: str
    score: Optional[float] = None
    explanation: Optional[Union[str, Dict[str, Any]]] = None

    class Config:
        extra = "ignore"


class CleanExperimentRun(BaseModel):
    """Execução de experimento limpa."""

    message_id: Optional[Union[str, int]] = None
    menssagem: Optional[str] = None
    golden_answer: Optional[str] = None
    model_response: Optional[str] = None
    reasoning_messages: List[ReasoningStep] = []
    metrics: List[Metric] = []

    class Config:
        extra = "ignore"


class ExperimentRunClean(BaseModel):
    """Dados limpos do experimento."""

    dataset_id: str
    experiment_id: str
    dataset_name: str
    experiment_name: str
    experiment_metadata: ExperimentMetadata
    experiment: List[CleanExperimentRun]

    class Config:
        extra = "ignore"
