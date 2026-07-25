# Platform Roadmap

This document outlines the milestones and completion statuses of the Meridian Revenue Copilot system.

---

## Completed Milestones

### Phase 1: Operational Automation
*   [x] **Milestone 1 — Stdio Gateway & Base Infrastructure**
    - Set up subprocess MCP gateways, JSON-RPC communication transport, and BaseRequest/BaseResponse contracts.
*   [x] **Milestone 2 — Intent Classification Tool**
    - Implemented rule-based query classifier.
*   [x] **Milestone 3 — Candidate Profiler Tool**
    - Designed LLM-based candidate profiler extracting role, seniority, and management taxonomies.

### Phase 2: Intelligence Layer
*   [x] **Milestone 4 — Deterministic Enrichment Service**
    - Implemented rules for timezone normalizations, clean emails/phones, and country codes.
*   [x] **Milestone 5 — Knowledge Platform (RAG)**
    - Designed DocumentIndexer, chunking configs, local MockVectorStore, embedding providers, and ranking.
*   [x] **Milestone 6 — Qualification Scoring Service**
    - Built multi-dimensional alignment scores with confidence values.
*   [x] **Milestone 7 — Summarization Service**
    - Generated recruiter recruiter-facing executive summaries using Scorer output.

### Phase 3: State & Agentic Layer
*   [x] **Milestone 8 — Context Builder**
    - Implemented pure composition builder compiling immutable `ContextSnapshot` models.
*   [x] **Milestone 9 — Memory Service**
    - Persisting `ContextSnapshot` files to abstract memory stores with merge policies.

---

## Planned Milestones

### Phase 3: State & Agentic Layer (Continued)
*   [ ] **Milestone 10 — Agent Orchestrator**
    - Designing conversational controllers routing sub-agent tasks.
*   [ ] **Milestone 11 — Planner**
    - Planning reasoning nodes coordinating evaluation sequences.
*   [ ] **Milestone 12 — Conversation Memory**
    - Session-based conversation histories.

### Phase 4: Production Integration
*   [ ] **Milestone 13 — Interview Intelligence**
    - Evaluating transcript files against candidate capabilities.
*   [ ] **Milestone 14 — Recruiter Copilot Front-End**
    - Recruiter portal, dashboard telemetry interfaces.
