import re
from typing import Tuple, Optional

# Basic regex for email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def normalize_email(email_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes a raw email address.
    Returns (normalized_value, source, confidence, validation_status, evidence).
    """
    if not email_str:
        return None, "email_normalizer", 1.0, "unverified", ["No email provided"]
        
    cleaned = email_str.strip().lower()
    
    # Validation Stage
    if EMAIL_REGEX.match(cleaned):
        return cleaned, "email_normalizer", 1.0, "valid", ["Email fits syntax standard regex pattern"]
    else:
        return cleaned, "email_normalizer", 0.5, "invalid", ["Email does not fit standard regex pattern"]

def extract_domain(email_str: Optional[str]) -> Optional[str]:
    """
    Extracts domain part of an email address.
    """
    if not email_str:
        return None
    cleaned = email_str.strip().lower()
    if "@" in cleaned:
        parts = cleaned.split("@")
        if len(parts) == 2:
            return parts[1]
    return None
