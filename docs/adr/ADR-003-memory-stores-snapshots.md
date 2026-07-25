# ADR-003

## Title

Memory Stores ContextSnapshots

---

## Status

Accepted

---

## Date

2026-07-25

---

## Context

As we design the Memory Service (Milestone 9), we must define what data representation is stored inside long-term retrieval systems. If we persist unstructured chatbot conversations or raw text files, we lose the structured metadata compiled by our intelligence pipelines.

---

## Decision

We propose that the Memory Service persists and retrieves **immutable `ContextSnapshot`** objects rather than raw conversations or isolated strings.

Specifically:
1. Every memory record is wrapped in a `MemorySnapshot` schema containing `MemoryMetadata` (creation/access timestamps, importance weights, tags, access counters) and the canonical `ContextSnapshot`.
2. Storage operations will write the entire snapshot to abstract backends (pgvector, local files).
3. Retrieval queries can match by specific sections of the snapshot (such as searching tech facts or matching executive summaries).

---

## Consequences

### Advantages

- **High-Fidelity Memory**: Recruiter bots can inspect not just past recommendations, but the exact qualification scores, facts, and evidences that justified them at that moment.
- **Pluggable backends**: Storing the snapshot as a unified record makes it trivial to map to document databases or object stores.

### Disadvantages

- **Redundant details storage**: Multiple snapshots for the same session might contain identical inputs or JD texts. This will be mitigated by implementing delta-storage or reference structures.

---

## Alternatives Considered

1. **Text Logs Storage**: Storing simple conversation transcripts. This is rejected because it requires future models to re-extract facts from logs.
2. **Normalized DB tables**: Shredding the snapshot into relational database tables. This is rejected because schema migrations would become extremely complex.

---

## Related Components

- `MemoryService`
- `MemoryProvider`
- `MemoryStore`
- `ContextSnapshot`

---

## Related Milestones

- Milestone 9 — Memory Service
- Milestone 12 — Conversation Memory

---

## Future Considerations

We can integrate semantic vector search over the reasoning block of the snapshot in future phases.
