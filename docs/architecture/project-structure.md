# Project Structure

This document outlines the codebase directories and module responsibilities of the Meridian Revenue Copilot repository.

---

## 1. Directory Layout

```text
meridian-copilot/
├── docs/                      # Central engineering documentation
│   ├── architecture/          # Architecture overviews, roadmap, layouts
│   ├── walkthroughs/          # Milestone implementation logs
│   ├── adr/                   # Architecture Decision Records
│   └── decisions/             # Deferred ideas and future trade-offs
│
├── src/
│   ├── services/              # Node.js gateway clients and facades
│   │   ├── mcpClient.js       # Stdio transport subprocess coordinator
│   │   ├── intelligenceGateway.js # Front-facing unified facade client
│   │   └── ...Client.js       # Domain-specific client adapters
│   │
│   └── intelligence/          # Core Python intelligence platform
│       ├── platform/          # Shared infrastructure (contracts, dotenv config, telemetry)
│       ├── mcp/               # FastMCP server entrypoint (server.py)
│       └── tools/             # Domain intelligence tools and services
│           ├── intent_classifier/
│           ├── candidate_profiler/
│           ├── deterministic_enricher/
│           ├── knowledge_service/
│           ├── qualification_scorer/
│           ├── summarizer/
│           └── context_builder/
│
├── tests/                     # Node.js (E2E gateway script verifications) and Python (pytest) suites
└── requirements.txt           # Python dependency file
```

---

## 2. Directory Responsibilities

### A. `docs/`
- Serves as the developer documentation hub. It contains diagrams, ADR entries, and step-by-step milestone verification details.

### B. `src/services/` (Node.js)
- Responsible for connecting external UI or API systems to the Python subprocesses. 
- Wraps stdio transport handshakes into clean, type-safe promise APIs.

### C. `src/intelligence/platform/` (Python)
- Contains zero-dependency shared classes. This includes request envelopes (`contracts.py`), environmental configs (`config.py`), and error logs/telemetry formats (`telemetry.py`).

### D. `src/intelligence/tools/` (Python)
- The domain business logic layer. Each subfolder (e.g. `summarizer/`, `context_builder/`) follows a clean provider-service schema separation:
  - `schema.py`: Extracted data interfaces.
  - `provider.py`: LLM reasoning, PromptLoader templates, and database adapters.
  - `service.py`: High-level service composition and factory builders.
