# ADR-011

## Title

Replay & Debug Framework separating Tracing Interceptors, Comparison Analysis, and Lineage Lineage

---

## Status

Accepted

---

## Date

2026-07-29

---

## Context

To debug failures, evaluate prompts, test newer code, or analyze regressions across model version upgrades, developers need a way to reproduce historical execution sessions exactly as they occurred.
This requires capturing inputs, configuration targets, outputs, context snapshots, and cost/resource tracking metrics without introducing performance overhead to core runtime inference.
Additionally, we need to track how replayed runs evolve over time (lineage) and calculate analytical diff summaries between runs.

---

## Decision

We design and implement a decoupled Replay & Debug Framework:
1. **Lineage Tracking**: Introduce `parent_replay_id` in `ReplayRecord` to establish parent-child relationships, linking replayed runs back to their ancestors.
2. **Interception Tracing**: Support automatic interceptors using a `@replay_capture` decorator for general functions, and a `ReplayCaptureHook` subclassing `EvaluationHook` to capture evaluation traces without modifying tool logic.
3. **Difference Analyzer**: Compares execution runs on cost, latency, confidence, reasoning logs, and exact output matches.
4. **Report Storage Drivers**: Separate storage contracts (`ReplayStorage`) from local flat-file storage implementation (`LocalFilesystemStorage`) to ensure compatibility with future SQL database or cloud object store expansions.

---

## Consequences

### Advantages

- Lineage lineage makes it easy to trace how predictions changed over iterations of re-evaluation.
- Tracing is fully automated using hooks and decorators, eliminating the need to modify existing codebase functions.
- Highly extensible storage.

### Disadvantages

- Writing intermediate run metadata consumes local disk space if sweeps are not cleaned up.

---

## Alternatives Considered

1. Directly execute run scripts manually in shells. Rejected as it fails to capture execution context metadata (like resource RAM, CPU, or cost metrics).

---

## Related Components

- `src/intelligence/tools/replay_debug/`
- `src/intelligence/mcp/server.py`
- `src/services/replayClient.js`
- `src/services/intelligenceGateway.js`

---

## Related Milestones

- Milestone 16 — Replay & Debug

---

## Future Considerations

- Web UI dashboards showing visualization diffs between original and replayed candidate profiles or qualification scores.
