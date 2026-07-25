# ADR-002

## Title

ContextSnapshot is the Canonical State Object

---

## Status

Accepted

---

## Date

2026-07-25

---

## Context

As the platform scales to support agentic reasoning (Milestone 10/11), conversation history tracking (Milestone 12), and conversational memories (Milestone 9), we need a structured schema to pass state between services. If every service uses its own ad-hoc model, the interface boundaries become bloated and hard to maintain.

---

## Decision

We establish `ContextSnapshot` as the **canonical representation of application state** inside the Meridian Revenue Copilot repository.

Specifically:
1. Future milestones—including the Memory Service, Planner, Agent Orchestrator, Conversation Memory, and Recruiter Copilot—must consume or operate on `ContextSnapshot` payload models.
2. The snapshot is strictly partitioned into distinct sections: `metadata`, `inputs`, `facts`, `evidence`, `reasoning`, and `outputs`.
3. `ContextSnapshot` models are treated as **immutable**. New information compiled from downstream workflows yields a new snapshot version, rather than mutating an existing snapshot object.

---

## Consequences

### Advantages

- **Unified Interface**: Downstream components only need to understand one single consolidated type schema (`ContextSnapshot`).
- **Audit & Replay Capability**: Immutability ensures that snapshots can be stored sequentially (e.g. inside `MemoryService`) to perfectly replay, evaluate, or debug the candidate evaluation process.
- **Clear Separation of Concerns**: Partitioning the snapshot structure decouples raw parameters (`inputs`), normalized properties (`facts`), LLM justifications (`evidence`/`reasoning`), and final data structs (`outputs`).

### Disadvantages

- **Larger Payload Overheads**: Passing the entire unified snapshot between services can produce larger data transport sizes. This is mitigated by offering options to exclude heavy fields (like `raw_text`) during long-term storage or network transfer.

---

## Alternatives Considered

1. **State Mutation**: Allowing downstream services to modify fields directly on a shared context object. This was rejected because it introduces concurrency issues and breaks audit tracking.
2. **Individual Service Output Passing**: Passing isolated models (e.g. only passing `QualificationPayload` to the Planner, and `SummarizationPayload` to the Memory service). This was rejected because it forces every service to know the details of all other service interfaces.

---

## Related Components

- `ContextSnapshot`
- `ContextMetadata`
- `ContextFacts`
- `ContextEvidence`
- `ContextReasoning`
- `ContextOutputs`

---

## Related Milestones

- Milestone 8 — Context Builder
- Milestone 9 — Memory Service
- Milestone 10 — Agent Orchestrator
- Milestone 11 — Planner
- Milestone 12 — Conversation Memory
- Milestone 14 — Recruiter Copilot

---

## Future Considerations

We can introduce utility helper methods on the `ContextSnapshot` model to export pruned versions tailored to LLM prompts to fit token limit constraints.
