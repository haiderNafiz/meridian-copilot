import time
from typing import Dict
from .schema import OpportunityIntelligenceRequest, OpportunityIntelligenceResult, AssessmentType
from .evidence.analyzer import EvidenceAnalyzer
from .policy.confidence import ConfidencePolicy
from .recommendation.builder import RecommendationBuilder
from .strategy.base import OpportunityAssessmentStrategy

class OpportunityIntelligenceProvider:
    def __init__(
        self,
        analyzer: EvidenceAnalyzer,
        confidence_policy: ConfidencePolicy,
        rec_builder: RecommendationBuilder,
        strategies: Dict[AssessmentType, OpportunityAssessmentStrategy]
    ):
        self.analyzer = analyzer
        self.confidence_policy = confidence_policy
        self.rec_builder = rec_builder
        self.strategies = strategies

    def generate_assessment(
        self,
        request: OpportunityIntelligenceRequest
    ) -> OpportunityIntelligenceResult:
        start_time = time.perf_counter()
        
        # 1. Analyze evidence
        evidence = self.analyzer.analyze_evidence(request.context_snapshot)
        
        # 2. Build recommendations
        actions = self.rec_builder.build_recommendations(
            risks=evidence["risks"],
            blockers=evidence["blockers"],
            missing=evidence["missing_information"]
        )
        evidence["recommended_next_actions"] = actions
        
        # 3. Calculate confidence
        enrich_conf = 1.0
        qual_conf = 1.0
        if "DeterministicEnrichmentService" in request.context_snapshot.metadata.provenance:
            enrich_conf = 0.9
            
        qual_payload = request.context_snapshot.outputs.qualification_scores if request.context_snapshot.outputs else None
        if qual_payload:
            scores = getattr(qual_payload, "scores", {})
            overall = scores.get("overall_qualification")
            if overall:
                qual_conf = getattr(overall, "confidence", 1.0)
                
        conv_quality = 1.0
        if request.conversation_context:
            conv_quality = 0.9
            
        confidence = self.confidence_policy.calculate_confidence(
            enrichment_confidence=enrich_conf,
            qualification_confidence=qual_conf,
            evidence_completeness=evidence["evidence_completeness"],
            conversation_context_quality=conv_quality
        )
        evidence["evidence_completeness"] = confidence
        
        # 4. Resolve strategy
        strategy = self.strategies.get(request.assessment_type)
        if not strategy:
            strategy = self.strategies[AssessmentType.CANDIDATE]
            
        assessment = strategy.assess(
            snapshot=request.context_snapshot,
            conv_context=request.conversation_context,
            evidence_summary=evidence
        )
        
        assessment.confidence = confidence
        
        latency = (time.perf_counter() - start_time) * 1000
        assessment.telemetry["latency_ms"] = latency
        
        from src.intelligence.platform.contracts import ResponseStatus
        from src.intelligence.platform.metadata import ResponseMetadata
        
        res_metadata = ResponseMetadata(
            provider="opportunity_intelligence_service",
            model="default_strategy",
            prompt_version="1.0.0",
            confidence=confidence,
            fallback_used=False,
            provider_latency_ms=latency
        )
        
        return OpportunityIntelligenceResult(
            assessment=assessment,
            status=ResponseStatus.SUCCESS,
            metadata=res_metadata
        )
