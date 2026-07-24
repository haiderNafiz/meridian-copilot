from typing import List, Tuple, Optional
from ..constants.technologies import TECH_KEYWORDS_SYNONYMS

def normalize_technologies(tech_list: Optional[List[str]]) -> Tuple[Optional[List[str]], str, float, str, list]:
    """
    Cleans, deduplicates, and canonicalizes technology keywords.
    """
    if not tech_list:
        return None, "technologies_normalizer", 1.0, "unverified", ["No technologies provided"]
        
    evidence = []
    normalized_set = set()
    has_synonyms = False
    
    for tech in tech_list:
        cleaned = tech.strip()
        lower_tech = cleaned.lower()
        if lower_tech in TECH_KEYWORDS_SYNONYMS:
            canonical = TECH_KEYWORDS_SYNONYMS[lower_tech]
            normalized_set.add(canonical)
            if canonical != cleaned:
                has_synonyms = True
                evidence.append(f"Mapped variation '{cleaned}' to canonical tech '{canonical}'")
        else:
            # Title-cased fallback if not in taxonomy map
            canonical = cleaned.title()
            normalized_set.add(canonical)
            
    res_list = sorted(list(normalized_set))
    confidence = 1.0 if not has_synonyms else 0.8
    evidence.append(f"Deduplicated technology list into {len(res_list)} items")
    
    return res_list, "technologies_normalizer", confidence, "valid", evidence
