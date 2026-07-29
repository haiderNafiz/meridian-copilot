# ADR-012: Human Feedback Platform

## Status
Accepted

## Context
Meridian needs a reusable, domain-agnostic Human Feedback Platform to capture, validate, normalize, and process feedback across all current and future intelligence tools, pipelines, and agents.
This feedback must support reinforcement learning integrations, golden dataset promotion, and reviewer consensus checks.

## Decision
We introduce the following core components in `src/intelligence/tools/human_feedback/`:
1. **FeedbackTarget**: Decoupled abstraction representing any target tool, workflow, pipeline, or agent using unique target IDs and target types.
2. **FeedbackRecord**: Immutable structure containing metadata, lineage links (`replay_id`, `evaluation_id`, `run_id`), and reviewers.
3. **FeedbackStrategy**: Pluggable strategies validating and normalizing feedback types (ratings, outcomes, annotations, preference, corrections).
4. **FeedbackEvent & FeedbackPipeline**: Lightweight event framework executing processors/hooks when a feedback is recorded.
5. **ConsensusStrategy**: Strategies computing agreement rates and resolving/marking disputes across multiple reviewer inputs.
6. **AnalyticsRegistry**: Extensible registry executing custom metric computations.
7. **DatasetPromotionWorkflow**: Coordinates strategy-based `PromotionPolicy` evaluation. Approved items are promoted to versioned, immutable dataset revision files (e.g. `v1_rev1.json`) to keep evaluation datasets reproducible.
8. **Audit Trail**: Saves history logs to track all submissions, reviews, and dataset promotions.

## Consequences
- System feedback can be collected across all pipeline modules without modification to core code.
- Evaluators can safely run evaluations against versioned, immutable datasets.
- Clear traceability of model improvement iterations is logged in the audit trail.
