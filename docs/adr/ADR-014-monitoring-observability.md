# ADR-014: AI Monitoring & Observability Platform Design

## Status

Accepted

## Date

2026-07-29

## Context

Production-level deployments of Meridian require comprehensive observability, tracing, health strategies, and metric collection to detect latency spikes, accuracy drops, regressions, and resource depletion. Furthermore, simple JSON array writes suffer from write amplification and data corruption hazards, calling for a durable, append-only storage strategy.

## Decision

We introduce the AI Monitoring & Observability Platform structured with the following layers:
1. **MonitoredComponent**: Directory of observed tasks and systems.
2. **MetricRegistry**: Tracks numeric attributes using `Counter`, `Gauge`, `Histogram`, and `Timer` definitions.
3. **TraceContext**: A nested tracking block and async/sync decorator helpers to record durations, outcomes, and tags without leaking open spans.
4. **AlertingEngine**: Handles thresholds and accuracy drops with alert deduplication and cooldown policies.
5. **LocalFilesystemStorageProvider**: An append-only JSONL storage engine ensuring high-performance durability.
6. **DashboardDataAggregator**: Data aggregation layer compiling SLA levels, percentiles, and counts without presentation coupling.
7. **FastMCP Integration**: Exposing status, metrics, events, health, alerts, and tracing handlers directly to the Node.js Gateway.

## Consequences

- Improved tracking and troubleshooting of pipeline failures.
- Robust metric capturing without blocking database overhead.
- Alerting mechanisms containing spam throttling safeguards.
