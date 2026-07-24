from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.intelligence.platform.contracts import BaseRequest, BaseResponse

class EnrichmentInput(BaseRequest):
    company_name: Optional[str] = Field(default=None, description="Raw company name")
    website: Optional[str] = Field(default=None, description="Raw company website URL")
    email: Optional[str] = Field(default=None, description="Raw email address")
    linkedin_url: Optional[str] = Field(default=None, description="Raw LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="Raw GitHub profile URL")
    phone_number: Optional[str] = Field(default=None, description="Raw telephone number")
    country: Optional[str] = Field(default=None, description="Raw country string or abbreviation")
    location: Optional[str] = Field(default=None, description="Raw location string (e.g., 'San Francisco, CA')")
    technology_keywords: Optional[List[str]] = Field(default=None, description="List of technical keywords")
    other_fields: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra structured parameters")

class FieldResult(BaseModel):
    normalized_value: Any = Field(description="The parsed, clean canonical value")
    source: str = Field(description="Deterministic utility/rule source identifier")
    confidence: float = Field(description="Confidence rating based on certainty of rule match")
    validation_status: str = Field(description="Field status: 'valid', 'invalid', or 'unverified'")
    evidence: List[str] = Field(default_factory=list, description="Rule matches or reasons for this transformation")

class EnrichmentPayload(BaseModel):
    # Normalized Fields
    company_name: Optional[FieldResult] = None
    website: Optional[FieldResult] = None
    email: Optional[FieldResult] = None
    linkedin_url: Optional[FieldResult] = None
    github_url: Optional[FieldResult] = None
    phone_number: Optional[FieldResult] = None
    country: Optional[FieldResult] = None
    technology_keywords: Optional[FieldResult] = None
    
    # Enrichments (Derived Values)
    timezone: Optional[FieldResult] = None
    company_domain: Optional[FieldResult] = None

class EnrichmentOutput(BaseResponse):
    payload: EnrichmentPayload
