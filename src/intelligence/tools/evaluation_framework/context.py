from pydantic import BaseModel
from typing import Dict, Any, Optional
from .schema import EvaluationConfig, EvaluationDataset

class EvaluationContext(BaseModel):
    run_id: str
    experiment_id: str
    session_id: Optional[str] = None
    dataset: EvaluationDataset
    config: EvaluationConfig
    environment: Dict[str, Any] = {}
