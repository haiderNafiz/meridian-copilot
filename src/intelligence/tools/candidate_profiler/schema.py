from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from src.intelligence.platform.contracts import BaseRequest

ROLE_TYPE_TAXONOMY = Literal["Backend", "Frontend", "Data", "DevOps", "Security", "ML", "PM", "Design", "Full-Stack"]
SENIORITY_TAXONOMY = Literal["Junior", "Mid", "Senior", "Staff", "Lead", "Director"]
URGENCY_TAXONOMY = Literal["passive_looker", "actively_interviewing", "immediate"]
MANAGEMENT_LEVEL_TAXONOMY = Literal["IC", "Lead", "Manager", "Senior Manager", "Director", "VP", "Executive", "Unknown"]

class EntityType(str, Enum):
    CANDIDATE = "candidate"
    LEAD = "lead"
    ACCOUNT = "account"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    GENERIC = "generic"

class EntityProfile(BaseModel):
    entity_type: EntityType = Field(default=EntityType.GENERIC, description="Type of entity")
    contacts: List[str] = Field(default_factory=list, description="Associated contact information")
    organization: Optional[str] = Field(default=None, description="Associated organization or company")
    location: Optional[str] = Field(default=None, description="Primary location")
    technologies: List[str] = Field(default_factory=list, description="Associated technical stack keywords")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific attributes")
    signals: Dict[str, Any] = Field(default_factory=dict, description="Generic telemetry, extraction, or audit signals")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and extraction metadata")

class CandidateInput(BaseRequest):
    raw_text: str = Field(description="Combined candidate fields (notes, cover letter, resume details)")
    current_title: Optional[str] = Field(default=None, description="Optional current professional title of the candidate")
    skills: Optional[List[str]] = Field(default=None, description="Optional list of core candidate skills")
    years_experience: Optional[int] = Field(default=None, ge=0, description="Optional total years of work experience")
    job_context: Optional[Dict[str, Any]] = Field(default=None, description="Optional job description/requirements dictionary for targeted profiling")

class CandidateProfile(EntityProfile):
    entity_type: EntityType = Field(default=EntityType.CANDIDATE, description="Type of entity")
    role_type: ROLE_TYPE_TAXONOMY
    seniority: SENIORITY_TAXONOMY
    urgency: URGENCY_TAXONOMY
    open_to_negotiation: bool
    predicted_functions: List[str] = Field(description="Normalized business capabilities or responsibilities (e.g. System Architecture, API Design, Mentorship) NOT job titles")
    technical_domains: List[str] = Field(description="High-level engineering domains (e.g. Cloud Infrastructure, Frontend Engineering, Distributed Systems, NLP) NOT specific tools or frameworks")
    management_level: MANAGEMENT_LEVEL_TAXONOMY
    evidence: List[str] = Field(description="Specific text snippets extracted from raw_text that support the profiling classification")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score representing classification accuracy")
    reasoning: str = Field(description="Brief textual rationale explaining taxonomy selections")

# Backward compatibility alias
CandidateOutput = CandidateProfile
