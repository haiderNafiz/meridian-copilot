from typing import Optional, List, Dict
from src.intelligence.tools.context_builder.schema import (
    ContextSnapshot,
    ContextFacts,
    ContextEvidence,
    ContextReasoning,
    ContextOutputs
)
from .base import MemoryPolicy

class MergeSnapshotPolicy(MemoryPolicy):
    def apply(self, existing: Optional[ContextSnapshot], new_incoming: ContextSnapshot) -> ContextSnapshot:
        if not existing:
            return new_incoming
        
        # 1. Merge Facts
        facts = ContextFacts(
            role_type=new_incoming.facts.role_type or existing.facts.role_type,
            seniority=new_incoming.facts.seniority or existing.facts.seniority,
            technical_domains=list(set(existing.facts.technical_domains + new_incoming.facts.technical_domains)),
            normalized_technologies=list(set(existing.facts.normalized_technologies + new_incoming.facts.normalized_technologies)),
            timezone=new_incoming.facts.timezone or existing.facts.timezone,
            country=new_incoming.facts.country or existing.facts.country
        )
        
        # 2. Merge Evidence
        scoring_ev = dict(existing.evidence.scoring_evidence)
        for k, v in new_incoming.evidence.scoring_evidence.items():
            if k in scoring_ev:
                scoring_ev[k] = list(set(scoring_ev[k] + v))
            else:
                scoring_ev[k] = v
                
        evidence = ContextEvidence(
            profile_evidence=list(set(existing.evidence.profile_evidence + new_incoming.evidence.profile_evidence)),
            scoring_evidence=scoring_ev
        )
        
        # 3. Merge Reasoning
        scoring_reas = dict(existing.reasoning.scoring_reasoning)
        scoring_reas.update(new_incoming.reasoning.scoring_reasoning)
        
        reasoning = ContextReasoning(
            scoring_reasoning=scoring_reas,
            summary_reasoning=new_incoming.reasoning.summary_reasoning or existing.reasoning.summary_reasoning,
            weaknesses_or_risks=new_incoming.reasoning.weaknesses_or_risks or existing.reasoning.weaknesses_or_risks,
            recruiter_recommendation=new_incoming.reasoning.recruiter_recommendation or existing.reasoning.recruiter_recommendation
        )
        
        # 4. Merge Outputs (newest values overlay existing)
        outputs = ContextOutputs(
            qualification_scores=new_incoming.outputs.qualification_scores or existing.outputs.qualification_scores,
            recruiter_summary=new_incoming.outputs.recruiter_summary or existing.outputs.recruiter_summary
        )
        
        return ContextSnapshot(
            metadata=new_incoming.metadata,
            inputs=new_incoming.inputs,
            facts=facts,
            evidence=evidence,
            reasoning=reasoning,
            outputs=outputs
        )
