# ADR-013: Production Knowledge Platform

## Status
Accepted

## Context
Meridian needs a unified, extensible, and domain-agnostic Production Knowledge Platform to manage ingestion, chunking, embedding, indexing, retrieval, and analytics of context assets across pipelines, agents, and workflows.

## Decision
We introduce the following core components in `src/intelligence/tools/knowledge_platform/`:
1. **Asset & Chunk Hierarchy**: Ingested content is modeled as `KnowledgeAsset` containing namespace, version logs, and asset derivation lineage (`derived_from_asset_id` separately from `parent_version_id`). It is chunked into `KnowledgeChunk` containing vector embeddings and source lineage references.
2. **ChunkStrategy**: Pluggable chunking strategies implementing custom splitters (e.g. paragraph, sliding window) registered in a pluggable strategy structure.
3. **EmbeddingRegistry**: Decoupled registry tracking embedding models, sizes, namespaces, and generating mock/live vector embeddings.
4. **IndexRegistry**: Replaceable keyword and vector index registries storing and consolidated partitions per namespace.
5. **MetadataFilterStrategy**: Decoupled multi-attribute filters enabling namespace-level, score-level, tag-level, and date-level constraints.
6. **RetrievalStrategy**: Pluggable dense, sparse, and hybrid retrieval logic combining vector cosine distances and token intersections.
7. **RankingEngine & RRF**: Consolidates dense and sparse outputs using Reciprocal Rank Fusion (RRF) algorithm.
8. **IngestionPipeline & Hooks**: Linear ingestion stages executing hook events (`before_ingestion`, `after_chunking`, `before_embedding`, `after_embedding`, `before_index`, `after_index`).
9. **KnowledgeAnalyticsRegistry**: Extensible calculators tracking namespace size, storage growth, retrieval precision, recall, and chunk reuse frequency.

## Consequences
- Dynamic knowledge ingestion and semantic/keyword retrieval is unified under a single stable interface (`KnowledgeQuery`).
- Metadata filtering can be scaled independently without modifying core retrieval routines.
- Ingestion stages are hook-extensible, permitting telemetry, validation, or compliance decorators to be easily attached.
