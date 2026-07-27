# ADR-004: Agent Orchestrator coordinates execution

## Status

Accepted

---

## Date

2026-07-27

---

## Context

The intelligence layer includes multiple discrete tools (Intent Classifier, Candidate Profiler, Deterministic Enricher, Knowledge Service, Qualification Scorer, Summarization Service, and Context Builder). Executing these sequentially manually in a hardcoded client logic is fragile, hard to test, and lacks centralized failure policies, retry policies, and execution traces. 

A component was needed to orchestrate tool executions deterministically without containing the business logic of each individual tool.

---

## Decision

We introduced the `AgentOrchestrator` pattern.
1. The orchestrator separates coordination (`AgentOrchestratorProvider`) from individual tool registration (`ToolRegistry`) and execution (`ToolExecutor`).
2. The orchestrator exposes dynamic dependency mapping using step outcomes stored inside a centralized `ExecutionContext`.
3. Standard retry policies (`RetryPolicy`) and failure strategies (`FailurePolicy`) are wrapped around steps.

---

## Consequences

### Advantages

- Decouples client workflows from hardcoded service calls.
- Provides standard telemetry, logging, and performance metrics across the entire pipeline.
- Handles partial failures gracefully using configurable fallback and abort policies.

### Disadvantages

- Incremental debugging latency when tracing inputs through dot-notation context mappings.

---

## Related Components

- `AgentOrchestratorProvider`
- `SimpleToolRegistry`
- `DirectToolExecutor`

---

## Related Milestones

- Milestone 10: Agent Orchestrator
