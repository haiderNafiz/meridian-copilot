from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.intelligence.platform.contracts import BaseRequest, BaseResponse

class SummaryType(str, Enum):
    CANDIDATE = "candidate"
    COMPANY = "company"
    LEAD = "lead"
    SALES_OPPORTUNITY = "sales_opportunity"
    MEETING = "meeting"
    EMAIL = "email"

class SummarizationInput(BaseRequest):
    raw_text: str = Field(description="Raw candidate profile or biography text")
    job_description_id: str = Field(description="Target job description ID to match against")
    email: Optional[str] = Field(default=None, description="Candidate email identifier")
    location: Optional[str] = Field(default=None, description="Candidate location details")
    technology_keywords: Optional[list] = Field(default_factory=list, description="Relevant technology keywords list")
    
    # Future compatibility config
    summary_type: SummaryType = Field(default=SummaryType.CANDIDATE, description="Type of summary to generate")
    additional_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata dictionary for other summary types")

class FactualSection(BaseModel):
    evidence: List[str] = Field(description="Objective statements of fact extracted from source profiles or enrichments")
    reasoning: str = Field(description="Generative reasoning describing the impact or context of those facts")

class SummarizationPayload(BaseModel):
    summary_type: SummaryType = Field(description="The type of summary outputted")
    executive_summary: str = Field(description="Concise 2-3 sentence recruiter overview of the candidate")
    strengths: FactualSection = Field(description="Candidate strengths grounded in evidence and reasoning")
    weaknesses_or_risks: FactualSection = Field(description="Identified qualification risks or gaps")
    recruiter_recommendation: str = Field(description="Actionable next step recommendation for recruiters")
    interview_focus: List[str] = Field(description="Key technical or cultural areas to assess during screening")
    follow_up_questions: List[str] = Field(description="Behavioral questions designed to clarify identified gaps")

class SummarizationOutput(BaseResponse):
    payload: SummarizationPayload
    provider_chain: List[str] = Field(default_factory=list, description="Pipeline nodes traversed to form the summary")
    retrieved_chunks: List[str] = Field(default_factory=list, description="Job description segment chunk IDs used")
