import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from src.intelligence.platform.contracts import BaseResponse

class TargetType(str, Enum):
    TOOL = "tool"
    WORKFLOW = "workflow"
    PIPELINE = "pipeline"
    AGENT = "agent"
    CUSTOM = "custom"

class FeedbackType(str, Enum):
    RATING = "rating"
    CORRECTION = "correction"
    ANNOTATION = "annotation"
    OUTCOME = "outcome"
    PREFERENCE = "preference"

class PromotionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class FeedbackTarget(BaseModel):
    target_id: str
    target_type: TargetType
    version: str = "latest"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FeedbackRecord(BaseModel):
    feedback_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4().hex[:10]}")
    run_id: str
    replay_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    target: FeedbackTarget
    reviewer_id: Optional[str] = None
    timestamp: str
    feedback_type: FeedbackType
    feedback_payload: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = "v1"

class FeedbackEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"fbev_{uuid.uuid4().hex[:10]}")
    feedback_id: str
    target: FeedbackTarget
    timestamp: str
    payload_snapshot: Any

class PromotionRequest(BaseModel):
    promotion_id: str = Field(default_factory=lambda: f"promo_{uuid.uuid4().hex[:10]}")
    replay_id: str
    target_domain: str
    target_dataset_type: str
    target_version: str
    status: PromotionStatus = PromotionStatus.PENDING
    created_at: str
    reviewed_by: Optional[str] = None

class AuditRecord(BaseModel):
    audit_id: str = Field(default_factory=lambda: f"aud_{uuid.uuid4().hex[:10]}")
    entity_id: str
    actor_id: str
    action: str
    timestamp: str
    changes: Dict[str, Any] = Field(default_factory=dict)

class FeedbackResponse(BaseResponse):
    feedback_record: Optional[FeedbackRecord] = None
    feedback_records: Optional[List[FeedbackRecord]] = None
    promotion_request: Optional[PromotionRequest] = None
    audit_record: Optional[AuditRecord] = None
    analytics_summary: Optional[Dict[str, Any]] = None
