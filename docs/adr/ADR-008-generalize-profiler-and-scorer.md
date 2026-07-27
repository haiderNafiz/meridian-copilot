# ADR-008

## Title

Generalizing Profiler and Scorer Services via Strategy Patterns

---

## Status

Accepted

---

## Date

2026-07-27

---

## Context

The Meridian platform is transitioning from a recruiting-focused copilot to a generalized Multimodal Revenue Intelligence Copilot. Hardcoded recruiting-specific implementations of the Candidate Profiler and Qualification Scorer services prevent the evaluation of other business entities (e.g. Leads, Accounts, Customers). We need a mechanism to support multiple domain-specific profiles and scoring models without modifying the underlying service and orchestrator components.

---

## Decision

Introduce Strategy Pattern abstractions for both profile extraction and qualification scoring:

1. **Profile Extraction**:
   - Introduce `EntityType` enum (`CANDIDATE`, `LEAD`, `ACCOUNT`, `CUSTOMER`, `VENDOR`, `GENERIC`).
   - Define a generic base `EntityProfile` Pydantic model.
   - Refactor `CandidateOutput` to subclass `EntityProfile` (renamed to `CandidateProfile` with a backwards-compatible type alias `CandidateOutput = CandidateProfile`).
   - Define `ProfileExtractionStrategy` abstract base and move candidate logic to `CandidateProfileStrategy`.

2. **Qualification Scoring**:
   - Define `QualificationStrategy` abstract base.
   - Move candidate scoring logic into `CandidateQualificationStrategy`.
   - Update `QualificationScorerService` to delegate execution to the injected strategy.

3. **Backward Compatibility**:
   - Maintain service constructor signatures using proxy properties and overloaded constructor wrappers that handle legacy providers/services seamlessly.

---

## Consequences

### Advantages

- **Domain-Agnostic Core**: The core services are generalized and completely decoupled from domain-specific rules.
- **High Extensibility**: New strategies (e.g. `LeadProfileStrategy`, `LeadQualificationStrategy`) can be plugged in without touching service or provider code.
- **Zero Downstream Regressions**: Perfect compatibility with downstream tools (Context Builder, Opportunity Intelligence, Planner, Orchestrator) and E2E Node.js verification scripts.

### Disadvantages

- Slight increase in strategy interface boilerplate, though this is heavily compensated by clean architectural decoupling.

---

## Related Components

- `CandidateProfilerService`
- `QualificationScorerService`
- `ProfileExtractionStrategy`
- `QualificationStrategy`

---

## Related Milestones

- Milestone 13.5: Domain-Agnostic Generalization Refactor
- Milestone 14: Revenue Copilot
