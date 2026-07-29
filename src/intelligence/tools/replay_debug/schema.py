import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from src.intelligence.platform.contracts import BaseResponse

class ReplayRecord(BaseModel):
    replay_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:10]}")
    parent_replay_id: Optional[str] = None  # Replay lineage tracking
    run_id: str
    target_id: str
    timestamp: str
    version: str
    input_payload: Any
    output_payload: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    prompts: Optional[Dict[str, str]] = None
    retrieved_documents: Optional[List[Dict[str, Any]]] = None
    reproducibility: Optional[Dict[str, Any]] = None
    cost: Optional[Dict[str, Any]] = None
    resource: Optional[Dict[str, Any]] = None

class ReplayExecutionResult(BaseModel):
    replay_id: str
    replayed_at: str
    output_payload: Any
    cost: Optional[Dict[str, Any]] = None
    resource: Optional[Dict[str, Any]] = None
    config_overridden: bool = False
    reproducibility: Optional[Dict[str, Any]] = None

class ReplayDiff(BaseModel):
    replay_id: str
    outputs_match: bool
    output_diff: Dict[str, Any]
    cost_delta: float
    duration_delta_ms: float
    confidence_delta: float
    reasoning_diff: Optional[str] = None

class ReplayResponse(BaseResponse):
    replay_record: Optional[ReplayRecord] = None
    execution_result: Optional[ReplayExecutionResult] = None
    diff: Optional[ReplayDiff] = None
    report_path: Optional[str] = None
