from typing import Tuple, Optional
from ..constants.countries import ISO_COUNTRY_MAP
from ..constants.geography import COUNTRY_TIMEZONE_MAP, CITY_TIMEZONE_MAP

def normalize_country(country_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Maps variations of country names to canonical country names.
    """
    if not country_str:
        return None, "geography_normalizer", 1.0, "unverified", ["No country provided"]
        
    cleaned = country_str.strip().lower()
    
    # Check map
    if cleaned in ISO_COUNTRY_MAP:
        canonical = ISO_COUNTRY_MAP[cleaned]
        return canonical, "geography_normalizer", 1.0, "valid", [f"Mapped variation '{country_str}' to canonical country '{canonical}'"]
        
    # Check title case fallback
    title_case = country_str.strip().title()
    return title_case, "geography_normalizer", 0.5, "unverified", [f"Defaulted to title-cased fallback country '{title_case}'"]

def infer_timezone(normalized_country: Optional[str], location_str: Optional[str]) -> Tuple[Optional[str], str, float, str, list]:
    """
    Infers timezone based on normalized country and location coordinates.
    """
    evidence = []
    
    # 1. Match city timezone first from location string if provided
    if location_str:
        loc_lower = location_str.lower()
        for city, tz in CITY_TIMEZONE_MAP.items():
            if city in loc_lower:
                evidence.append(f"Inferred timezone '{tz}' matching city keyword '{city}' in location string")
                return tz, "geography_normalizer", 0.8, "valid", evidence
                
    # 2. Match country timezone default if country is matched
    if normalized_country and normalized_country in COUNTRY_TIMEZONE_MAP:
        tz = COUNTRY_TIMEZONE_MAP[normalized_country]
        evidence.append(f"Inferred default timezone '{tz}' for country '{normalized_country}'")
        return tz, "geography_normalizer", 1.0, "valid", evidence
        
    evidence.append("No matching timezone rules found for country or location")
    return None, "geography_normalizer", 1.0, "unverified", evidence
