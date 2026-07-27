# ADR-007

## Title

Opportunity Intelligence is Decoupled and Strategy-Driven

---

## Status

Accepted

---

## Date

2026-07-27

---

## Context

The copilot system has evolved from a recruiting-only platform to a generalized multimodal revenue intelligence copilot. 

Domain evaluation logic must not run inside intermediate tool wrappers or be embedded directly in the orchestrator. Further, domain assessments must be evidence-driven and support multiple entities (e.g. Lead, Account, Candidate, Customer, Deal).

---

## Decision

Introduce Opportunity Intelligence service. It consumes only structured snapshot and conversation context states. It leverages an `EvidenceAnalyzer` to compute completeness, a deterministic `ConfidencePolicy` for validation, and a strategy pattern abstraction (`OpportunityAssessmentStrategy`) to route evaluation.

The system is structured as:
1. `EvidenceAnalyzer`: audit input facts, check contradictions.
2. `ConfidencePolicy`: determine weighted assessment confidence.
3. `RecommendationBuilder`: prioritize next steps.
4. `OpportunityAssessmentStrategy`: map to output schemas.

---

## Consequences

### Advantages

- Decoupled from execution; can be called independently as an MCP tool.
- Zero runtime tool execution overhead.
- Highly extensible (just write new Strategy implementations for new domains).
- Deterministic confidence metrics allow auditable score tracing.

### Disadvantages

- Requires pre-constructed context snapshot, so caller must orchestrate preceding components first.

---

## Alternatives Considered

1. Direct LLM prompting in orchestrator.
2. Recruiting-specific hardcoded tools.

---

## Related Components

- `OpportunityIntelligenceService`
- `EvidenceAnalyzer`
- `ConfidencePolicy`
- `RecommendationBuilder`

---

## Related Milestones

- Milestone 13: Opportunity Intelligence
- Milestone 14: Revenue Copilot

---

## Future Considerations

Support Account-specific and Deal-specific strategy pipelines.
