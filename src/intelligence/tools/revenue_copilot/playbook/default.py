from .base import PlaybookStrategy
from ..schema import PlaybookRecommendation, PlaybookCategory
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment

class DefaultPlaybookStrategy(PlaybookStrategy):
    def select_playbook(self, assessment: OpportunityAssessment) -> PlaybookRecommendation:
        score = getattr(assessment, "opportunity_score", 0.5)
        
        # Generalize category selection from assessment properties
        if score >= 0.7:
            category = PlaybookCategory.EVALUATION
            name = getattr(assessment, "recommended_plan", "technical_interview")
            objective = "Fast-track technical alignment and schedule direct review."
        elif score < 0.4:
            category = PlaybookCategory.DISCOVERY
            name = getattr(assessment, "recommended_plan", "client_followup")
            objective = "Gather missing requirements or context variables."
        else:
            category = PlaybookCategory.QUALIFICATION
            name = getattr(assessment, "recommended_plan", "candidate_screening")
            objective = "Run initial screening to verify qualification dimensions."
            
        return PlaybookRecommendation(
            category=category,
            playbook_name=name,
            confidence=getattr(assessment, "confidence", 0.8),
            objective=objective
        )
