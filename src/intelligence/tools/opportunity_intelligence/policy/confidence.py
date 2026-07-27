from typing import Dict, Any

class ConfidencePolicy:
    def calculate_confidence(
        self,
        enrichment_confidence: float,
        qualification_confidence: float,
        evidence_completeness: float,
        conversation_context_quality: float = 1.0
    ) -> float:
        """Deterministic combination of confidence signals."""
        weights = {
            "enrichment": 0.2,
            "qualification": 0.3,
            "completeness": 0.4,
            "conversation": 0.1
        }
        
        weighted_score = (
            (enrichment_confidence * weights["enrichment"]) +
            (qualification_confidence * weights["qualification"]) +
            (evidence_completeness * weights["completeness"]) +
            (conversation_context_quality * weights["conversation"])
        )
        
        return round(max(0.0, min(1.0, weighted_score)), 2)
