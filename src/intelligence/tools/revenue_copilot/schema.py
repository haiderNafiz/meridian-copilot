from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.context_builder.schema import ContextSnapshot
from src.intelligence.tools.conversation_memory.schema import ConversationContext
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment

class PlaybookCategory(str, Enum):
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    EVALUATION = "evaluation"
    NEGOTIATION = "negotiation"
    FOLLOW_UP = "follow_up"
    RETENTION = "retention"

class PlaybookRecommendation(BaseModel):
    category: PlaybookCategory = Field(description="Universal playbook stage category")
    playbook_name: str = Field(description="Domain-specific playbook workflow name (e.g. candidate_screening)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in selection correctness")
    objective: str = Field(description="Core business outcome targeted by this playbook")

class ActionChecklist(BaseModel):
    critical_actions: List[str] = Field(default_factory=list, description="Top-priority blocker resolutions")
    required_actions: List[str] = Field(default_factory=list, description="Missing information retrieval actions")
    advisory_actions: List[str] = Field(default_factory=list, description="Mitigations and standard reviews")

class DraftCommunication(BaseModel):
    subject: Optional[str] = Field(default=None, description="Communication subject or title")
    body: str = Field(description="Generated draft text body (email, notes, agenda)")
    recipient_group: str = Field(description="Target audience (e.g. candidate, lead, CRM, internal)")

class FollowUpQuestion(BaseModel):
    question: str = Field(description="Dialogue clarifying question")
    intent_target: str = Field(description="Target missing profile attribute to resolve")

class ExplanationSummary(BaseModel):
    rationale: str = Field(description="Structured business reasoning block")
    evidence_backed: List[str] = Field(default_factory=list, description="Supporting factual snippets")

class CopilotRecommendation(BaseModel):
    playbook: PlaybookRecommendation
    checklist: ActionChecklist
    drafts: List[DraftCommunication] = Field(default_factory=list)
    follow_up_questions: List[FollowUpQuestion] = Field(default_factory=list)
    explanation: ExplanationSummary

class RevenueCopilotRequest(BaseRequest):
    opportunity_assessment: OpportunityAssessment = Field(description="Preceding opportunity assessment")
    context_snapshot: ContextSnapshot = Field(description="Structured context snapshot")
    conversation_context: Optional[ConversationContext] = Field(default=None, description="Consolidated conversation context history")

class RevenueCopilotResult(BaseResponse):
    recommendation: CopilotRecommendation = Field(description="Assembled action and playbook recommendations")
    status: str = Field(default="success")
