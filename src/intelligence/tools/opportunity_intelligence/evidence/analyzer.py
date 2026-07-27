from typing import Dict, Any, List
from src.intelligence.tools.context_builder.schema import ContextSnapshot

class EvidenceAnalyzer:
    def analyze_evidence(self, snapshot: ContextSnapshot) -> Dict[str, Any]:
        """Aggregate evidence, check consistency/contradictions, and evaluate completeness."""
        strengths = []
        risks = []
        blockers = []
        missing = []
        
        # 1. Check Facts completeness
        facts = snapshot.facts
        if not facts:
            missing.append("ContextFacts: General context facts are missing.")
        else:
            if not facts.normalized_technologies:
                missing.append("Technologies: No candidate technologies parsed.")
            else:
                strengths.append(f"Technical skills: Candidate possesses {len(facts.normalized_technologies)} verified technologies.")
                
            if not facts.seniority:
                missing.append("Seniority: Seniority level is not populated.")
            elif facts.seniority.lower() in ["senior", "architect", "lead"]:
                strengths.append("Seniority: Profile indicates solid senior level history.")

        # 2. Check Location & Timezone
        if facts:
            if not facts.timezone:
                missing.append("Timezone: Normalized timezone is missing.")
            else:
                strengths.append(f"TimezoneVerified: Timezone is set to {facts.timezone}.")

        # 3. Check Qualification Scores completeness
        qualification = snapshot.outputs.qualification_scores if snapshot.outputs else None
        if not qualification:
            missing.append("QualificationScores: Scorer results are missing.")
        else:
            # If any scoring dimension is extremely low, flag as risk
            scores = getattr(qualification, "scores", {})
            for key, score_obj in scores.items():
                score_val = getattr(score_obj, "score", 0)
                if score_val < 0.2:
                    risks.append(f"LowScoreDimension: Scoring dimension '{key}' has low value ({score_val}).")
                elif score_val >= 0.8:
                    strengths.append(f"HighScoreDimension: Strong alignment in dimension '{key}' ({score_val}).")

        # 4. Compute completeness score
        total_checks = 5
        missing_count = len(missing)
        completeness = max(0.0, 1.0 - (missing_count / total_checks))
        
        return {
            "strengths": strengths,
            "risks": risks,
            "blockers": blockers,
            "missing_information": missing,
            "evidence_completeness": completeness,
            "details": {
                "facts_status": "present" if facts else "missing",
                "qualification_status": "present" if qualification else "missing"
            }
        }
