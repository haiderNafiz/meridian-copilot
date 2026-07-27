# ADR-006: Separate Long-Term Memory from Conversation Memory

## Status

Accepted

---

## Date

2026-07-27

---

## Context

As the Meridian Revenue Copilot handles longer client interactions, loading the entire historical log of conversation context directly into the Planner would cause token context bloat and degraded performance.

We need a clear architectural boundary between persistent long-term storage and transient active working memory/session state management.

---

## Decision

We separated Long-Term Memory from Conversation Memory:
1. **MemoryService**: Serves as the authoritative, persistent, append-only long-term memory for `ContextSnapshot` records.
2. **Conversation Memory**: Operates as a transient, session-oriented layer managing short-term active Working Memory (turns, extracted entities, unresolved questions, pending actions).
3. **Planning Intake**: The `Planner` consumes a consolidated `ConversationContext` resolved by Conversation Memory, rather than querying the raw `MemoryService` directly.
4. **Decoupled API Routing**: Conversation Memory accesses the `MemoryService` exclusively via its public query and retrieval API endpoints.

---

## Consequences

### Advantages

- **Prevents Context Bloat**: Keeps the planner's token usage highly efficient by limiting inputs to a sliding conversation window and relevance-filtered persistent memories.
- **Improved Retrieval Efficiency**: Decouples short-term session states from persistent database operations.
- **Pluggable Selection**: Future semantic search and contextual relevance strategies can be swapped into the `MemorySelectionStrategy` without altering storage schemas.

### Disadvantages

- Serializing transient session state to database records requires deliberate workflow save-points (e.g. `save_memory` orchestrator nodes).

---

## Related Components

- `MemoryService`
- `ConversationMemoryService`
- `MemoryRetriever`
- `MemorySelectionStrategy`
- `PlannerService`

---

## Related Milestones

- Milestone 9: Memory Service
- Milestone 12: Conversation Memory
