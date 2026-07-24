import re
from typing import Tuple, Optional
from urllib.parse import urlparse

# Basic regex for URL validation (checking for protocol/host presence)
URL_REGEX = re.compile(r"^(https?://)?[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def normalize_website(url_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes a website URL.
    Returns (normalized_value, source, confidence, validation_status, evidence).
    """
    if not url_str:
        return None, "website_normalizer", 1.0, "unverified", ["No website provided"]
        
    cleaned = url_str.strip()
    
    # Validation Stage
    if not URL_REGEX.match(cleaned):
        return cleaned, "website_normalizer", 0.5, "invalid", ["Invalid URL syntax pattern"]
        
    evidence = []
    # Ensure scheme is present
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        cleaned = "https://" + cleaned
        evidence.append("Prepend default 'https://' scheme")
        
    # Trim trailing slashes
    while cleaned.endswith("/"):
        cleaned = cleaned[:-1]
        
    evidence.append("Cleaned trailing slashes and spaces")
    return cleaned, "website_normalizer", 1.0, "valid", evidence

def normalize_linkedin(url_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes a LinkedIn profile URL to https://www.linkedin.com/in/{username} format.
    """
    if not url_str:
        return None, "linkedin_normalizer", 1.0, "unverified", ["No LinkedIn URL provided"]
        
    cleaned = url_str.strip()
    evidence = []
    
    # Check if is simple username
    if "/" not in cleaned and "." not in cleaned:
        username = cleaned.lower()
        cleaned = f"https://www.linkedin.com/in/{username}"
        evidence.append("Constructed URL from simple username")
        return cleaned, "linkedin_normalizer", 1.0, "valid", evidence
        
    # Parse URL
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        cleaned = "https://" + cleaned
        evidence.append("Prepended default protocol")
        
    parsed = urlparse(cleaned)
    if "linkedin.com" not in parsed.netloc:
        return url_str, "linkedin_normalizer", 0.5, "invalid", ["Not a linkedin.com profile URL"]
        
    path = parsed.path
    # Extract username from path like /in/username
    match = re.search(r"/in/([^/]+)", path, re.IGNORECASE)
    if match:
        username = match.group(1).lower()
        cleaned_url = f"https://www.linkedin.com/in/{username}"
        evidence.append("Parsed canonical username from LinkedIn profile path")
        return cleaned_url, "linkedin_normalizer", 1.0, "valid", evidence
    else:
        # Fallback
        return cleaned, "linkedin_normalizer", 0.7, "unverified", ["Could not find canonical /in/ path format"]

def normalize_github(url_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Normalizes a GitHub profile URL to https://github.com/{username} format.
    """
    if not url_str:
        return None, "github_normalizer", 1.0, "unverified", ["No GitHub URL provided"]
        
    cleaned = url_str.strip()
    evidence = []
    
    # Check if is simple username
    if "/" not in cleaned and "." not in cleaned:
        username = cleaned.lower()
        cleaned = f"https://github.com/{username}"
        evidence.append("Constructed URL from simple username")
        return cleaned, "github_normalizer", 1.0, "valid", evidence
        
    # Parse URL
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        cleaned = "https://" + cleaned
        evidence.append("Prepended default protocol")
        
    parsed = urlparse(cleaned)
    if "github.com" not in parsed.netloc:
        return url_str, "github_normalizer", 0.5, "invalid", ["Not a github.com profile URL"]
        
    path = parsed.path.strip("/")
    parts = path.split("/")
    if parts and parts[0]:
        username = parts[0].lower()
        cleaned_url = f"https://github.com/{username}"
        evidence.append("Parsed GitHub username from profile path")
        return cleaned_url, "github_normalizer", 1.0, "valid", evidence
    else:
        return cleaned, "github_normalizer", 0.7, "unverified", ["Could not find GitHub username in path"]
