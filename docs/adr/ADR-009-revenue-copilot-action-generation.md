# ADR-009

## Title

Separating Action Generation from Opportunity Assessment

---

## Status

Accepted

---

## Date

2026-07-27

---

## Context

Opportunity Assessment (Milestone 13) focuses on evidence aggregation, score normalization, and evaluating domain suitability. Tightly coupling task checklists, dialogue follow-ups, and communication drafting directly within the assessment phase limits reuse. To enable a highly scalable multimodal copilot, action planning and document drafting must be separated into a distinct, modular stage.

---

## Decision

Introduce the **Revenue Copilot** as a separate downstream intelligence step that consumes `OpportunityAssessment` and outputs prioritized checklists, playbooks, and draft content:

1. **Strategic Playbook Mapping**:
   - Classify universal playbook category stages (`DISCOVERY`, `QUALIFICATION`, `EVALUATION`, `NEGOTIATION`, `FOLLOW_UP`, `RETENTION`) separately from domain-specific execution plan names.
   
2. **Format-Specific Communication Strategies**:
   - Split content drafting logic into a registry of `CommunicationStrategy` modules: `EmailStrategy`, `CRMStrategy`, `AgendaStrategy`, and `ProposalStrategy`.
   - Avoid monolithic template generators by delegating output generation to these modular strategy classes.

---

## Consequences

### Advantages

- **High Separation of Concerns**: Opportunity Intelligence evaluates *what* the status is; Revenue Copilot determines *how* to react.
- **Registry-Based Extension**: New communication formats (e.g. Slack alerts, DocuSign wrappers) can be added as strategies without modifying existing codebase.
- **Clean Schema Design**: Distinct input and output contracts prevent context pollution.

### Disadvantages

- Slights increases the payload size through the pipeline, though mitigated by modular schemas.

---

## Related Components

- `RevenueCopilotService`
- `PlaybookStrategy`
- `CommunicationStrategy`
- `ActionPlanner`

---

## Related Milestones

- Milestone 14: Revenue Copilot
