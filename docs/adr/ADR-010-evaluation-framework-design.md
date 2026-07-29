# ADR-010

## Title

Evaluation Framework Design separating Execution Target, Scoring Strategy, and Dataset Registry

---

## Status

Accepted

---

## Date

2026-07-29

---

## Context

We need an extensible evaluation framework to measure the quality, correctness, and performance of all Meridian components (such as prompt tools, agents, workflow chains, and external API interfaces).
Existing designs combined execution (running the model/tool) with scoring/metric computation. This made it difficult to:
1. Re-use scoring logic (e.g. classification accuracy, BLEU score, robustness perturbation testing) across different execution targets.
2. Evaluate new abstractions (like multi-agent pipelines or whole workflows) without modifying metric calculation code.
3. Manage evaluation datasets and run historical regression delta reports efficiently.

---

## Decision

We introduce three clean abstractions to separate execution, target selection, and scoring:
1. **`EvaluationTarget`**: The interface representing a component to be executed (e.g. `ToolTarget` wrapping an MCP tool).
2. **`EvaluationRunner`**: Executes target invocations in batch while collecting runtime stats (RAM, CPU, latency).
3. **`EvaluationStrategy`**: Individual scoring components (e.g. `ClassificationStrategy`, `FairnessStrategy`, `RobustnessStrategy`) that compute `MetricResult` structures comparing predictions with targets.

We also establish a structured `DatasetRegistry` to discover datasets under domain folders, and a `ReportStore` to save JSON and Markdown reports with baseline regression checks.

---

## Consequences

### Advantages

- Extremely flexible execution: We can evaluate tools, agents, or entire pipelines without changing how metrics are calculated.
- Complete domain-agnostic and metric-agnostic architecture: New metrics (e.g. fairness demographic parity, citation explainability) can be added as strategies in a strategy registry.
- Regression testing is deterministic and decoupled from execution.

### Disadvantages

- Extra model mapping boilerplate.

---

## Alternatives Considered

1. Directly execute python tool functions in the main evaluation service loop. Rejected because it restricts non-python tool executions (like external APIs or Node.js workers).
2. Store datasets as database rows. Rejected in favor of local JSON flat-file storage under organized folders to facilitate git tracking.

---

## Related Components

- `src/intelligence/tools/evaluation_framework/`
- `src/intelligence/mcp/server.py`
- `src/services/intelligenceGateway.js`

---

## Related Milestones

- Milestone 15 — Evaluation Framework

---

## Future Considerations

- Automated continuous integration triggers comparing test branch reports with production master baselines.
