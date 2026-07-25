from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse
from src.intelligence.tools.candidate_profiler.schema import CandidateOutput
from src.intelligence.tools.deterministic_enricher.schema import EnrichmentOutput
from src.intelligence.tools.qualification_scorer.schema import QualificationPayload
from src.intelligence.tools.summarizer.schema import SummarizationPayload
from src.intelligence.tools.knowledge_service.schema import RetrievalResult

class ContextMetadata(BaseModel):
    context_id: str = Field(description="Immutable state tracker ID (UUID or unique session code)")
    session_id: Optional[str] = Field(default=None, description="Conversational session identifier")
    schema_version: str = Field(default="1.0.0", description="ContextSnapshot versioning tracker")
    timestamp_utc: datetime = Field(description="Snapshot compilation UTC timestamp")
    provenance: List[str] = Field(default_factory=list, description="Executing nodes/services that contributed details")
    overall_confidence: float = Field(default=1.0, description="Confidence rating compiled across contributors")

class ContextInputs(BaseModel):
    document_references: List[str] = Field(default_factory=list, description="List of source resume/JD references")
    # TODO (Phase 3 Memory): Treat raw_text as transient processing content. 
    # Long-term conversational storage systems should reference document_references instead of persisting large text blobs.
    raw_text: Optional[str] = Field(default=None, description="Optional raw candidate text input")

class ContextFacts(BaseModel):
    role_type: Optional[str] = Field(default=None, description="Extracted primary role profile")
    seniority: Optional[str] = Field(default=None, description="Extracted seniority level")
    technical_domains: List[str] = Field(default_factory=list, description="Core technical engineering domains")
    normalized_technologies: List[str] = Field(default_factory=list, description="Normalized tech keywords")
    timezone: Optional[str] = Field(default=None, description="Normalized timezone compatibility code")
    country: Optional[str] = Field(default=None, description="Normalized candidate country")

class ContextEvidence(BaseModel):
    profile_evidence: List[str] = Field(default_factory=list, description="Factual segments backing the profile")
    scoring_evidence: Dict[str, List[str]] = Field(default_factory=dict, description="Factual matches backing scoring dimensions")

class ContextReasoning(BaseModel):
    scoring_reasoning: Dict[str, str] = Field(default_factory=dict, description="Recruiter explanation behind scoring dimensions")
    summary_reasoning: Optional[str] = Field(default=None, description="Recruiter executive summary reasoning")
    weaknesses_or_risks: Optional[str] = Field(default=None, description="Reasoning behind qualification risks or gaps")
    recruiter_recommendation: Optional[str] = Field(default=None, description="Actionable next step recommendation")

class ContextOutputs(BaseModel):
    qualification_scores: Optional[QualificationPayload] = Field(default=None, description="Qualification Scorer payload")
    recruiter_summary: Optional[SummarizationPayload] = Field(default=None, description="Summarizer payload")

class ContextSnapshot(BaseModel):
    metadata: ContextMetadata
    inputs: ContextInputs
    facts: ContextFacts
    evidence: ContextEvidence
    reasoning: ContextReasoning
    outputs: ContextOutputs

class ContextBuilderInput(BaseRequest):
    context_id: str = Field(description="Unique contextual snapshot tracker ID")
    session_id: Optional[str] = Field(default=None, description="Session mapping identifier")
    document_references: List[str] = Field(default_factory=list, description="List of source document references")
    raw_text: Optional[str] = Field(default=None, description="Optional raw candidate text input")
    
    # Pre-calculated service outputs (Supporting partial context mapping if empty/None)
    candidate_profile: Optional[CandidateOutput] = Field(default=None, description="Candidate profiler service output")
    candidate_enrichment: Optional[EnrichmentOutput] = Field(default=None, description="Deterministic enrichment output")
    retrieved_context: Optional[List[RetrievalResult]] = Field(default=None, description="Knowledge platform results context list")
    qualification_scores: Optional[QualificationPayload] = Field(default=None, description="Qualification Scorer payload")
    recruiter_summary: Optional[SummarizationPayload] = Field(default=None, description="Recruiter summary payload")

class ContextBuilderOutput(BaseResponse):
    payload: ContextSnapshot
    provider_chain: List[str] = Field(default_factory=list, description="Trace sequence of contributors")
