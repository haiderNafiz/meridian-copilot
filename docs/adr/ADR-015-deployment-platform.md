# ADR-015: Deployment Platform Design

## Status

Accepted

## Date

2026-07-30

## Context

Production operations require a centralized entry point to deploy, bootstrap, validate version compatibility, catalog installed plugins, monitor lifecycle transitions, and trigger rollbacks. Business logic needs to remain strictly decoupled from infrastructure concerns. Additionally, direct storage writes to observability logs should be avoided by using passive event handlers.

## Decision

We introduce the Deployment Platform structured as follows:
1. **Pydantic Contracts (`schema.py`)**: Defines rich system models including `DeploymentManifest` (platform constraints), `PlatformManifest` (platform identity card), and `ValidationResult` (checks stats).
2. **Version Resolution (`resolver.py`)**: Checks dependency constraints via `VersionResolver` and `CompatibilityMatrix`.
3. **Pluggable Validators (`strategy/validation.py`)**: Employs a `ValidationRegistry` mapping validators (`StartupValidator`, `DependencyValidator`, `HealthValidator`, `ProductionReadinessValidator`), ensuring extensible verification checks.
4. **LocalFilesystemDeploymentStorageProvider (`provider/file.py`)**: Stores configurations and manifest logs in high-performance append-only JSONL files.
5. **Passive Observability Handlers**: Logs system bootstrap events (`BOOTSTRAP_STARTED`, `PROFILE_LOADED`, `DEPENDENCIES_VALIDATED`, `PLUGIN_REGISTERED`, `BOOTSTRAP_COMPLETED`, etc.) to the AI Monitoring & Observability Platform passively.
6. **FastMCP Server & Node Gateway Integration**: Exposes deployment endpoints to the gateway for E2E verification.

## Consequences

- Completely decoupled backend orchestration.
- Standardized, consistent pluggable validation registry pattern.
- Pure deployment agnosticism with direct passive events tracing.
