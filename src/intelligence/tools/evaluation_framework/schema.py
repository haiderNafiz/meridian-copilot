from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.platform.metadata import ResponseMetadata

class DatasetType(str, Enum):
    CURATED = "curated"
    SYNTHETIC = "synthetic"
    BENCHMARK = "benchmark"
    REGRESSION = "regression"
    GOLDEN = "golden"

class MetricType(str, Enum):
    CLASSIFICATION = "classification"
    RANKING = "ranking"
    GENERATION = "generation"
    REASONING = "reasoning"
    WORKFLOW = "workflow"
    COST = "cost"
    RESOURCE = "resource"
    ROBUSTNESS = "robustness"
    FAIRNESS = "fairness"
    EXPLAINABILITY = "explainability"
    CALIBRATION = "calibration"

class EvaluationItem(BaseModel):
    id: str = Field(description="Unique check identifier")
    input_payload: Dict[str, Any] = Field(description="Parameters fed into target component")
    expected_output: Any = Field(description="Target ground truth value")
    tags: List[str] = Field(default_factory=list, description="Descriptive labels")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context constraints")

class MetricResult(BaseModel):
    metric_name: str = Field(description="Target metric identifier")
    score: float = Field(description="Normalized assessment score value")
    passed: bool = Field(description="Outcome against criteria threshold")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed scoring logs")

class ResourceMetrics(BaseModel):
    cpu_percent: float
    peak_ram_mb: float
    average_ram_mb: float
    duration_ms: float
    throughput_items_per_sec: float
    gpu_memory_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    disk_io: Optional[Dict[str, float]] = None
    network_io: Optional[Dict[str, float]] = None

class CostMetrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    embedding_tokens: int = 0
    estimated_cost: float = 0.0
    currency: str = "USD"
    provider: str

class ExecutionResult(BaseModel):
    actual_output: Any
    latency_ms: float
    cost: CostMetrics
    resource: ResourceMetrics
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Raw execution artifacts")

class EvaluationRunResult(BaseModel):
    item_id: str = Field(description="Reference to evaluation item")
    actual_output: Any = Field(description="Produced output")
    metrics: List[MetricResult] = Field(description="Computed metric results")
    resource: ResourceMetrics
    cost: CostMetrics
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)

class EvaluationDataset(BaseModel):
    dataset_id: str = Field(description="Unique dataset key")
    version: str = Field(description="Dataset release version")
    dataset_type: DatasetType
    items: List[EvaluationItem] = Field(description="Scenario checks list")

class ReproducibleConfig(BaseModel):
    random_seed: int = Field(default=42)
    model_version: str = Field(default="latest")
    embedding_version: Optional[str] = None
    provider: str = Field(default="groq")
    temperature: float = Field(default=0.0)
    top_p: float = Field(default=1.0)
    git_commit: Optional[str] = None
    platform_version: str = Field(default="1.0.0")

class FairnessConfig(BaseModel):
    protected_attributes: List[str] = Field(default_factory=list)
    comparison_groups: List[Dict[str, Any]] = Field(default_factory=list)
    acceptable_delta: float = Field(default=0.05)
    evaluation_method: str = Field(default="demographic_parity")

class EvaluationConfig(BaseModel):
    target_id: str
    metrics: List[MetricType] = Field(default_factory=list)
    reproducibility: ReproducibleConfig = Field(default_factory=ReproducibleConfig)
    fairness: Optional[FairnessConfig] = None
    thresholds: Dict[str, float] = Field(default_factory=dict)
    report_formats: List[str] = Field(default_factory=lambda: ["json", "markdown"])

class EvaluationReport(BaseModel):
    report_id: str = Field(description="Unique report key")
    run_id: str
    experiment_id: str
    dataset_id: str
    target_tool: str
    overall_score: float
    run_results: List[EvaluationRunResult]
    passed: bool
    recommendations: List[str] = Field(default_factory=list)
    created_at: str
    reproducibility: ReproducibleConfig
    cost_summary: CostMetrics
    resource_summary: ResourceMetrics

class EvaluationRequest(BaseRequest):
    dataset_id: str
    config: EvaluationConfig
    experiment_id: Optional[str] = None

class EvaluationResult(BaseResponse):
    report: EvaluationReport
    status: str = "success"
