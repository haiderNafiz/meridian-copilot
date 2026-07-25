# ADR-001

## Title

Context Builder is a Pure Composition Service

---

## Status

Accepted

---

## Date

2026-07-25

---

## Context

During Phase 2 implementation of the intelligence layer (Intent Classifier, Candidate Profiler, Deterministic Enricher, Knowledge Platform, Qualification Scorer, and Summarizer), each component evolved its own schemas and processing rules. As we move to Phase 3 (Memory, Planning, Agent Orchestrator), the system requires a consolidated representation of all intelligence outputs to avoid duplicate retrieval and redundant orchestration calls.

We needed a clean architecture to compile this consolidated representation without hard-coupling the execution of sub-services.

---

## Decision

We implement the `ContextBuilderService` as a **pure composition service**. 

Specifically:
1. The service never triggers or executes Phase 2 services (such as profiling, scoring, or summarizing) directly inside its process loops.
2. It accepts already-computed service outputs as optional input fields in `ContextBuilderInput`.
3. It maps and merges these partial inputs safely into a consolidated, immutable `ContextSnapshot` structure.
4. If some fields are missing (partial context), it provides default empty/None values rather than throwing validation errors.

---

## Consequences

### Advantages

- **Decoupled Architecture**: Keeps the context building process completely decoupled from the service execution lifecycles and sequence ordering.
- **Zero Redundant Execution**: Different execution nodes or clients (such as the Node.js gateway) can trigger individual Phase 2 services independently, then build the snapshot without repeating vector search or LLM scoring.
- **Support for Partial Contexts**: Allows workflows to make snapshots when only a subset of Phase 2 tasks (e.g. only profiler and enricher) has run.

### Disadvantages

- **Orchestration Shift**: The responsibility of executing Phase 2 services is shifted upstream to orchestrators (like the Node.js gateway/pipeline), meaning python client services are called individually before builder composition.

---

## Alternatives Considered

1. **Pipeline Execution Service**: Making the Context Builder run the profiler, enricher, scorer, and summarizer internally. This was rejected because it introduces duplicate orchestration layers, duplicate retrievals, and rigid ordering constraints.
2. **Untracked Dictionaries**: Merging everything into unstructured JSON objects. This was rejected because it breaks Type safety, validation schemas, and auto-generated API specifications.

---

## Related Components

- `ContextBuilderService`
- `ContextBuilderProvider`
- `ContextSnapshot`

---

## Related Milestones

- Milestone 8 — Context Builder
- Milestone 9 — Memory Service

---

## Future Considerations

As we scale, we can introduce automated pipeline controllers or custom schema adapters within the Node.js pipeline layer to make builder inputs creation automated.
