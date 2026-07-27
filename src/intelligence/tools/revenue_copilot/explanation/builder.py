from ..schema import ExplanationSummary
from src.intelligence.tools.opportunity_intelligence.schema import OpportunityAssessment

class ExplanationBuilder:
    def build_explanation(self, assessment: OpportunityAssessment) -> ExplanationSummary:
        rationale = (
            f"Opportunity Scored {assessment.opportunity_score} at {assessment.lifecycle_stage} stage. "
            f"Guidance recommendation: {assessment.decision_guidance}."
        )
        evidence = assessment.strengths + assessment.risks
        return ExplanationSummary(
            rationale=rationale,
            evidence_backed=evidence
        )
