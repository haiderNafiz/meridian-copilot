# Meridian Revenue Copilot - Engineering Documentation

Welcome to the central engineering documentation for **Meridian Revenue Copilot**. This directory serves as the single source of truth for the project's architecture, design decisions, milestone walkthroughs, and future roadmap.

---

## 1. Documentation Structure

The documentation is organized into four logical segments:

- **[`architecture/`](architecture/system-overview.md)**: Stable documents describing the system-level details, repository layout, overall structures, and milestone roadmaps.
- **[`walkthroughs/`](walkthroughs/README.md)**: Chronological implementation and verification records for each completed milestone.
- **[`adr/`](adr/README.md)**: Architecture Decision Records (ADRs) tracking the project's architectural history, constraints, and evolution.
- **[`decisions/`](decisions/README.md)**: Intentional trade-offs, deferred ideas, and research paths.

---

## 2. ADR Workflow

To ensure that major design choices are documented, peer-reviewed, and preserved, we follow a strict ADR lifecycle:

```text
Architecture Proposal & Review
             │
             ▼
   Implementation Completed
             │
             ▼
     Test Suite Passes
             │
             ▼
 Walkthrough Record Written
             │
             ▼
     ADR Authored & Indexed
             │
             ▼
     Milestone Frozen
```

For a template to format new ADRs, refer to [`docs/adr/TEMPLATE.md`](adr/TEMPLATE.md).
