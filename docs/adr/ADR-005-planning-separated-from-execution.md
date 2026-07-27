# ADR-005: Planning Is Separated from Execution

## Status

Accepted

---

## Date

2026-07-27

---

## Context

Initially, the orchestrator resolver determined the workflow plan and executed it together. Hardcoding the plan directly in the execution engine makes it impossible to support dynamic planning (such as rule-based routing, LLM-based planning, and hybrid workflows) without altering the orchestrator itself. 

To enable long-term maintainability, experimentation, and safety, we need a complete decoupling between plan compilation and execution.

---

## Decision

We separated Planning from Execution by introducing a compiler-like architecture:
1. **Planner Service**: Responsible exclusively for selecting or assembling workflow templates from requests, context, and memory logs. It validates required tools, state requirements, and configurations before execution starts. It never runs the tools itself.
2. **Agent Orchestrator**: Responsible exclusively for receiving a completed `ExecutionPlan` and coordinating its execution sequence.
3. **ExecutionPlan**: The stable contract and data exchange schema between the Planner and the Orchestrator.

---

## Consequences

### Advantages

- **Pluggable Planning Strategies**: Enables painless swap-ins of strategies (`RuleBasedPlanner`, `LLMPlanner`, `HybridPlanner`) without changes to the orchestrator.
- **Fail-Fast Safety**: Constraint validation catches missing or deactivated tools before execution starts, preventing runtime surprises.
- **Auditable & Replayable**: The execution plan can be logged, audited, replayed, and evaluated independently.

### Disadvantages

- Adds a serialization layer between plan compilation and orchestration run.

---

## Related Components

- `PlannerService`
- `PlannerStrategy`
- `ConstraintResolver`
- `WorkflowCatalog`
- `AgentOrchestratorService`

---

## Related Milestones

- Milestone 11: Planner
