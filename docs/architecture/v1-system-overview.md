# Meridian Multimodal Revenue Copilot — v1.0 Architecture Overview

This document presents the complete system architecture, data flow paths, milestone index, and dependency maps for the Meridian platform as of Milestone 14 (v1.0 release).

---

## 1. System Diagram

```mermaid
graph TD
    User([User Prompt / Input Channel]) --> Gateway[Intelligence Gateway]
    
    subgraph Phase 1: Operational Automation
        Gateway --> Intent[Intent Classifier]
    end

    subgraph Phase 2: Knowledge & Profiling
        Gateway --> Profiler[Profile Extraction Service]
        Gateway --> Enricher[Deterministic Enricher]
        Gateway --> Knowledge[Knowledge Platform / Retrieval]
        Gateway --> Scorer[Qualification Scorer]
        Gateway --> Summarizer[Summarization Service]
    end

    subgraph Phase 3: Dialogue, Opportunity & Copilot Action
        Gateway --> ContextBuilder[Context Builder]
        Gateway --> Memory[Memory Service / Conversation Memory]
        Gateway --> OppIntel[Opportunity Intelligence]
        Gateway --> RevenueCopilot[Revenue Copilot Service]
        Gateway --> Planner[Planner]
        Gateway --> Orchestrator[Agent Orchestrator]
    end

    %% Storage & Providers
    Profiler --> Providers[(Model / Storage Providers)]
    Knowledge --> Providers
    Memory --> Storage[(Long-Term Memory File Store)]
```

---

## 2. The 14 Milestones and Responsibilities

1. **Milestone 1: Intent Classifier** — Identifies intent and routes inbound interactions (Recruiting, Client, Support, etc.).
2. **Milestone 2: Candidate Profiler** — Evaluates unstructured textual resumes to extract role type, seniority, urgency, and technical skills.
3. **Milestone 3: Deterministic Enricher** — Normalizes emails, phone numbers, URLs, and timezone mappings via standard regex/canonical definitions.
4. **Milestone 4: Knowledge Platform** — Implements retrieval mechanisms, vector indexes, document chunking, and similarity ranking.
5. **Milestone 5: Qualification Scorer** — Scores profiles against specific target descriptions along multiple alignment dimensions.
6. **Milestone 6: Summarization Service** — Generates brief profiles summaries and bulleted structural highlights.
7. **Milestone 7: Service Orchestrator / Telemetry** — Captures JSON performance logging, tracking execution duration and LLM latency.
8. **Milestone 8: Context Builder** — Aggregates structured outputs from earlier stages into an immutable `ContextSnapshot`.
9. **Milestone 9: Memory Service** — Maintains an append-only long-term history of sessions and interactions.
10. **Milestone 10: Agent Orchestrator** — Executes selected execution steps utilizing resilient fallback policies.
11. **Milestone 11: Planner** — Translates user queries and constraints into executable sequential plans.
12. **Milestone 12: Conversation Memory** — Implements a sliding window session-oriented retrieval layer separate from long-term memory.
13. **Milestone 13: Opportunity Intelligence** — Translates fact matrices into structured opportunity score evaluations.
14. **Milestone 14: Revenue Copilot** — Maps evaluations to universal playbook categories, prioritizes action checklists, and drafts communications.

---

## 3. End-to-End Data Flow

```
[Inbound Raw Text]
       │
       ▼
1. Intent Classifier ────────────────► Classify category
       │
       ▼
2. Profile Extraction ───────────────► Extract structured facts & skills
       │
       ▼
3. Deterministic Enricher ───────────► Normalize emails, URLs & timezones
       │
       ▼
4. Retrieval Service ────────────────► Retrieve semantic context chunks
       │
       ▼
5. Qualification Scorer ─────────────► Score profile suitability
       │
       ▼
6. Summarization Service ────────────► Compile brief profile highlights
       │
       ▼
7. Context Builder ──────────────────► Compose unified ContextSnapshot
       │
       ▼
8. Memory Service ───────────────────► Fetch sliding-window context history
       │
       ▼
9. Opportunity Intelligence ─────────► Determine score & gaps
       │
       ▼
10. Revenue Copilot ─────────────────► Select playbook, checklists, and generate drafts
```

---

## 4. Architectural Decision Records (ADRs)

- [ADR-001 — Operational Automation Core Principles](../adr/ADR-001-operational-automation.md)
- [ADR-002 — Profile and Enrichment Services Decoupling](../adr/ADR-002-decouple-profiler-and-enricher.md)
- [ADR-003 — MCP Schema and Tool Gateway Protocol](../adr/ADR-003-mcp-integration.md)
- [ADR-004 — Context Building Immutable Snapshots](../adr/ADR-004-context-builder-immutable.md)
- [ADR-005 — Planning and Execution Decoupling](../adr/ADR-005-planning-separated-from-execution.md)
- [ADR-006 — Separate Long-Term Memory from Conversation Memory](../adr/ADR-006-separate-long-term-memory-from-conversation-memory.md)
- [ADR-007 — Decoupled Strategy-Driven Opportunity Intelligence](../adr/ADR-007-opportunity-intelligence.md)
- [ADR-008 — Generalizing Profiler and Scorer Services via Strategy Patterns](../adr/ADR-008-generalize-profiler-and-scorer.md)
- [ADR-009 — Separating Action Generation from Opportunity Assessment](../adr/ADR-009-revenue-copilot-action-generation.md)

---

## 5. Dependency Map of Services

```
┌────────────────────────────────┐
│      RevenueCopilotService     │
└───────────────┬────────────────┘
                │ depends on
                ▼
┌────────────────────────────────┐      ┌─────────────────────────────┐
│  OpportunityIntelligenceServ   ├─────►│    ContextBuilderService    │
└───────────────┬────────────────┘      └──────────────┬──────────────┘
                │ depends on                           │ builds from outputs of
                ▼                                      ▼
┌────────────────────────────────┐      ┌─────────────────────────────┐
│    ConversationMemoryService   │      │ QualificationScorerService  │
└────────────────────────────────┘      └──────────────┬──────────────┘
                                                       │ depends on
                                                       ▼
                                        ┌─────────────────────────────┐
                                        │  CandidateProfilerService   │
                                        └─────────────────────────────┘
```
