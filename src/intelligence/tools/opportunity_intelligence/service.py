from typing import Optional
from .schema import (
    OpportunityIntelligenceRequest, OpportunityIntelligenceResult, 
    AssessmentType, OpportunityAssessment
)
from .provider import OpportunityIntelligenceProvider

class OpportunityIntelligenceService:
    def __init__(self, provider: OpportunityIntelligenceProvider):
        self.provider = provider

    def assess(
        self,
        context_snapshot,
        conversation_context = None,
        assessment_type: AssessmentType = AssessmentType.CANDIDATE
    ) -> OpportunityIntelligenceResult:
        req = OpportunityIntelligenceRequest(
            context_snapshot=context_snapshot,
            conversation_context=conversation_context,
            assessment_type=assessment_type
        )
        return self.provider.generate_assessment(req)

_opportunity_intelligence_service = None

def get_opportunity_intelligence_service() -> OpportunityIntelligenceService:
    global _opportunity_intelligence_service
    if _opportunity_intelligence_service is None:
        from .evidence.analyzer import EvidenceAnalyzer
        from .policy.confidence import ConfidencePolicy
        from .recommendation.builder import RecommendationBuilder
        from .strategy.default import DefaultAssessmentStrategy
        
        analyzer = EvidenceAnalyzer()
        conf_policy = ConfidencePolicy()
        rec_builder = RecommendationBuilder()
        
        strategies = {
            AssessmentType.CANDIDATE: DefaultAssessmentStrategy()
        }
        
        provider = OpportunityIntelligenceProvider(
            analyzer=analyzer,
            confidence_policy=conf_policy,
            rec_builder=rec_builder,
            strategies=strategies
        )
        _opportunity_intelligence_service = OpportunityIntelligenceService(provider=provider)
    return _opportunity_intelligence_service
