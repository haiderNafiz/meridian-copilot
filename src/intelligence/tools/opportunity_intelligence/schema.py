from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from src.intelligence.tools.conversation_memory.schema import ConversationContext

class AssessmentType(str, Enum):
    CANDIDATE = "candidate"
    LEAD = "lead"
    ACCOUNT = "account"
    CUSTOMER = "customer"
    DEAL = "deal"
    GENERIC = "generic"

class OpportunityAssessment(BaseModel):
    assessment_type: AssessmentType = Field(description="Domain assessment type tag")
    business_intent: str = Field(description="Extracted target intent statement")
    lifecycle_stage: str = Field(description="Operational milestone stage description")
    confidence: float = Field(ge=0.0, le=1.0, description="Deterministic confidence score")
    opportunity_score: float = Field(ge=0.0, le=1.00, description="Overall strength alignment score")
    strengths: List[str] = Field(default_factory=list, description="Aggregated positive signals")
    risks: List[str] = Field(default_factory=list, description="Identified potential issues")
    blockers: List[str] = Field(default_factory=list, description="Critical process constraints")
    missing_information: List[str] = Field(default_factory=list, description="Unresolved required fields")
    evidence_summary: Dict[str, Any] = Field(default_factory=dict, description="Completeness diagnostics")
    recommended_next_actions: List[str] = Field(default_factory=list, description="Ranked priority next steps")
    recommended_plan: str = Field(description="Suggested copilot plan/playbook action routing")
    follow_up_items: List[str] = Field(default_factory=list, description="Dialogue follow-up questions")
    decision_guidance: str = Field(description="Recruiter/Manager action directive summary")
    explanation: str = Field(description="Explainable natural reasoning block")
    telemetry: Dict[str, Any] = Field(default_factory=dict, description="Latency and utilization statistics")

class OpportunityIntelligenceRequest(BaseRequest):
    context_snapshot: ContextSnapshot = Field(description="Preceding compiled context snapshot")
    conversation_context: Optional[ConversationContext] = Field(default=None, description="Consolidated conversation history context")
    assessment_type: AssessmentType = Field(default=AssessmentType.CANDIDATE, description="Target evaluation strategy selection type")

class OpportunityIntelligenceResult(BaseResponse):
    assessment: OpportunityAssessment = Field(description="Completed structured assessment object")
    status: str = Field(default="success")
