# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records tracking major design decisions and system evolution.

## ADR Index

| ADR | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| [ADR-001](ADR-001-context-builder.md) | Context Builder is a Pure Composition Service | Accepted | 2026-07-25 |
| [ADR-002](ADR-002-context-snapshot.md) | ContextSnapshot is the Canonical State Object | Accepted | 2026-07-25 |
| [ADR-003](ADR-003-memory-stores-snapshots.md) | Memory Stores ContextSnapshots | Proposed | 2026-07-25 |
| [ADR-004](ADR-004-agent-orchestrator.md) | Agent Orchestrator coordinates execution | Accepted | 2026-07-27 |
| [ADR-005](ADR-005-planning-separated-from-execution.md) | Planning Is Separated from Execution | Accepted | 2026-07-27 |
| [ADR-006](ADR-006-separate-long-term-memory-from-conversation-memory.md) | Separate Long-Term Memory from Conversation Memory | Accepted | 2026-07-27 |
| [ADR-007](ADR-007-opportunity-intelligence.md) | Opportunity Intelligence is Decoupled and Strategy-Driven | Accepted | 2026-07-27 |
| [ADR-008](ADR-008-generalize-profiler-and-scorer.md) | Generalizing Profiler and Scorer Services via Strategy Patterns | Accepted | 2026-07-27 |
| [ADR-009](ADR-009-revenue-copilot-action-generation.md) | Separating Action Generation from Opportunity Assessment | Accepted | 2026-07-27 |
| [ADR-010](ADR-010-evaluation-framework-design.md) | Evaluation Framework Design separating Execution Target, Scoring Strategy, and Dataset Registry | Accepted | 2026-07-29 |

---

## Guide to Writing ADRs

1. Copy [`docs/adr/TEMPLATE.md`](TEMPLATE.md) to a new file named `ADR-XXX-descriptive-name.md`.
2. Fill in the sections describing context, decision rationale, trade-offs, and consequences.
3. Update the ADR Index table in this file with the new record.
