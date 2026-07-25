# Future Ideas & Deferred Work

This document tracks intentional trade-offs, postponed improvements, and research directions compiled throughout the milestones development.

---

## 1. Knowledge Platform (RAG)
- **Pluggable Vector Store**: Migrating the abstract `VectorStore` from the initial mock in-memory index to pgvector, Chroma, or Qdrant without downstream scorers/summarizers modifications.
- **Dynamic Chunking Config**: Adding configurable chunking strategies (e.g. sentence splits, token splits, recursive text splits) to optimize retrieve context limits.

---

## 2. Telemetry and Provenance
- **Rich Monitoring (Phase 4)**: Enrolling detailed telemetry formats inside `provenance` records (tracking prompt template version numbers, exact model IDs, latency durations, and token usage) to feed dashboard interfaces.
- **Unified Tracing Correlation**: Link Node.js Gateway trace headers to Python backend telemetry lines via stdout JSON dumps.

---

## 3. Memory and State
- **Eviction and Decay Strategies**: Implement memory retention policies that decrease the `importance` score of older, unused snapshots.
- **Confidence Weights Aggregator**: Introduce weighted confidence formulas (e.g., weighing LLM scoring indicators higher than regex enricher flags) using a pluggable `ConfidenceStrategy` pattern.
