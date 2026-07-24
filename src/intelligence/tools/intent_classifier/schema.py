from pydantic import BaseModel, EmailStr
from typing import Literal
from src.intelligence.platform.contracts import BaseRequest


class IntentInput(BaseRequest):
    raw_text: str

    source: Literal[
        "email",
        "form",
        "file_upload"
    ]

    sender_email: EmailStr

#from pydantic import BaseModel


class IntentOutput(BaseModel):
    intent: str

    confidence: float

    fallback_used: bool

    reasoning: str


ALLOWED_INTENTS = [
    "new_candidate_application",
    "candidate_referral",
    "client_inquiry",
    "recruiter_outreach_reply",
    "status_check",
    "withdrawal",
    "spam",
    "unknown"
]