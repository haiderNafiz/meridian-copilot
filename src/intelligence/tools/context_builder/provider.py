from datetime import datetime, timezone
from .schema import (
    ContextSnapshot,
    ContextMetadata,
    ContextInputs,
    ContextFacts,
    ContextEvidence,
    ContextReasoning,
    ContextOutputs
)

class ContextBuilderProvider:
    def compose(self, request) -> ContextSnapshot:
        # TODO (Phase 4 Monitoring): Enrich provenance list to capture richer execution metrics 
        # (e.g. service versions, provider models, prompt versions, latency statistics)
        provenance = []
        confidence_vals = []
        
        if request.candidate_profile:
            provenance.append("CandidateProfilerService")
            confidence_vals.append(request.candidate_profile.confidence)
        if request.candidate_enrichment:
            provenance.append("DeterministicEnrichmentService")
            p = request.candidate_enrichment.payload
            if p.technology_keywords:
                confidence_vals.append(p.technology_keywords.confidence)
        if request.retrieved_context:
            provenance.append("KnowledgeService")
        if request.qualification_scores:
            provenance.append("QualificationScorerService")
            # Note: Qualification Scorer Enum dimensions or string mapping support
            for k, v in request.qualification_scores.scores.items():
                name = k.value if hasattr(k, "value") else str(k)
                if name == "overall_qualification":
                    confidence_vals.append(v.confidence)
        if request.recruiter_summary:
            provenance.append("SummarizationService")
            
        # TODO (Phase 3 Memory/Planning): Refactor confidence calculation into a pluggable 
        # ConfidenceStrategy or ConfidenceAggregator interface to support custom weighting
        overall_confidence = sum(confidence_vals) / len(confidence_vals) if confidence_vals else 1.0
        
        metadata = ContextMetadata(
            context_id=request.context_id,
            session_id=request.session_id,
            timestamp_utc=datetime.now(timezone.utc),
            provenance=provenance,
            overall_confidence=overall_confidence
        )
        
        inputs = ContextInputs(
            document_references=request.document_references,
            raw_text=request.raw_text
        )
        
        # Compile Facts (Partial contexts safe fallbacks)
        facts = ContextFacts()
        if request.candidate_profile:
            facts.role_type = request.candidate_profile.role_type
            facts.seniority = request.candidate_profile.seniority
            facts.technical_domains = request.candidate_profile.technical_domains
        if request.candidate_enrichment:
            p = request.candidate_enrichment.payload
            if p.technology_keywords:
                facts.normalized_technologies = p.technology_keywords.normalized_value or []
            if p.timezone:
                facts.timezone = p.timezone.normalized_value
            if p.country:
                facts.country = p.country.normalized_value
                
        # Compile Evidence
        evidence = ContextEvidence()
        if request.candidate_profile:
            evidence.profile_evidence = request.candidate_profile.evidence
        if request.qualification_scores:
            evidence.scoring_evidence = {
                k.value if hasattr(k, "value") else str(k): v.evidence
                for k, v in request.qualification_scores.scores.items()
            }
            
        # Compile Reasoning
        reasoning = ContextReasoning()
        if request.qualification_scores:
            reasoning.scoring_reasoning = {
                k.value if hasattr(k, "value") else str(k): v.reasoning
                for k, v in request.qualification_scores.scores.items()
            }
        if request.recruiter_summary:
            s = request.recruiter_summary
            reasoning.summary_reasoning = s.executive_summary
            if s.weaknesses_or_risks:
                reasoning.weaknesses_or_risks = s.weaknesses_or_risks.reasoning
            reasoning.recruiter_recommendation = s.recruiter_recommendation
            
        # Compile Outputs
        outputs = ContextOutputs(
            qualification_scores=request.qualification_scores,
            recruiter_summary=request.recruiter_summary
        )
        
        return ContextSnapshot(
            metadata=metadata,
            inputs=inputs,
            facts=facts,
            evidence=evidence,
            reasoning=reasoning,
            outputs=outputs
        )
