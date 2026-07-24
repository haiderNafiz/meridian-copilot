from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from src.intelligence.platform.contracts import BaseRequest, BaseResponse

class ScoringDimension(str, Enum):
    SKILL_MATCH = "skill_match"
    EXPERIENCE_MATCH = "experience_match"
    SENIORITY_MATCH = "seniority_match"
    DOMAIN_MATCH = "domain_match"
    LOCATION_COMPATIBILITY = "location_compatibility"
    EMPLOYMENT_TYPE_COMPATIBILITY = "employment_type_compatibility"
    AVAILABILITY_URGENCY = "availability_urgency"
    OVERALL_QUALIFICATION = "overall_qualification"

class QualificationInput(BaseRequest):
    raw_text: str = Field(description="Unstructured candidate resume/profile text")
    job_description_id: str = Field(description="Target job description ID to match against")
    email: Optional[str] = Field(default=None, description="Optional raw candidate email")
    location: Optional[str] = Field(default=None, description="Optional raw candidate location")
    technology_keywords: Optional[list] = Field(default_factory=list, description="Optional raw technologies list")

class DimensionScore(BaseModel):
    score: float = Field(description="Numeric score between 0.0 and 1.0 representing matching precision")
    confidence: float = Field(description="Confidence rating between 0.0 and 1.0 based on evidence presence")
    evidence: List[str] = Field(default_factory=list, description="Concrete objective facts extracted from raw text")
    reasoning: str = Field(description="Subjective analytical logic explaining the rating outcome")

class QualificationPayload(BaseModel):
    scores: Dict[ScoringDimension, DimensionScore] = Field(
        description="Structured scores indexed by target match dimension"
    )
    reconciliation_notes: str = Field(
        description="Detailed overview of how dimension variables shaped overall outcome"
    )

class QualificationOutput(BaseResponse):
    payload: QualificationPayload
    retrieved_chunks: List[str] = Field(
        default_factory=list,
        description="List of chunk_ids evaluated during scoring"
    )
    provider_chain: List[str] = Field(
        default_factory=list,
        description="Execution sequence of platform components forming this result"
    )
