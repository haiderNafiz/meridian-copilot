import re
from typing import Tuple, Optional

# Basic format patterns (at least 7 digits to be considered valid)
PHONE_DIGITS_REGEX = re.compile(r"^\+?[0-9]{7,15}$")

def normalize_phone(phone_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes telephone numbers.
    Returns (normalized_value, source, confidence, validation_status, evidence).
    """
    if not phone_str:
        return None, "phone_normalizer", 1.0, "unverified", ["No phone number provided"]
        
    cleaned = phone_str.strip()
    evidence = []
    
    # Strip spaces, dashes, dots, and parentheses
    digits_only = re.sub(r"[\s\-\.\(\)]", "", cleaned)
    
    if PHONE_DIGITS_REGEX.match(digits_only):
        if digits_only != cleaned:
            evidence.append("Stripped formatting characters (spaces, dashes, parentheses)")
            confidence = 1.0
        else:
            evidence.append("Phone number matches standard digit constraints directly")
            confidence = 1.0
        return digits_only, "phone_normalizer", confidence, "valid", evidence
    else:
        # Fallback for short or bad sequences
        evidence.append("Phone number did not match standard length constraints")
        return digits_only, "phone_normalizer", 0.6, "invalid", evidence
