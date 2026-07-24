import re
from typing import Tuple, Optional

# Regex for common legal suffix strings
SUFFIX_REGEX = re.compile(r"\b(inc|llc|ltd|corp|corporation|incorporated|gmbh|sa|pvt)\.?\b", re.IGNORECASE)

def normalize_company(name_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes company names by cleaning whitespace and matching canonical formats.
    """
    if not name_str:
        return None, "company_normalizer", 1.0, "unverified", ["No company name provided"]
        
    cleaned = name_str.strip()
    evidence = []
    
    # Remove extra spaces
    cleaned = " ".join(cleaned.split())
    
    # Strip common legal suffixes
    base_name = SUFFIX_REGEX.sub("", cleaned).strip()
    # Trim trailing/leading commas or dots left by suffixes
    base_name = base_name.rstrip(",. ").lstrip(",. ")
    
    if not base_name:
        # Fallback to cleaned if suffix stripping left nothing
        base_name = cleaned
        evidence.append("Kept original company name because suffix stripping cleared the string")
        confidence = 0.8
    else:
        if base_name != cleaned:
            evidence.append(f"Stripped corporate legal suffix from company name (base: '{base_name}')")
            confidence = 1.0
        else:
            evidence.append("Company name was clean, no corporate legal suffix found")
            confidence = 1.0
            
    return base_name, "company_normalizer", confidence, "valid", evidence
