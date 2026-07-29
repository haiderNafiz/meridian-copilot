import { mcpClient } from "./mcpClient.js";

export const knowledgePlatformClient = {
  /**
   * Ingest a document or dataset.
   */
  async ingestKnowledge(namespace, content, assetType, assetId = null, metadata = {}, version = "v1", parentVersionId = null, derivedFromAssetId = null) {
    const rawResult = await mcpClient.callTool("ingest_knowledge", {
      namespace,
      content,
      asset_type: assetType,
      asset_id: assetId,
      metadata,
      version,
      parent_version_id: parentVersionId,
      derived_from_asset_id: derivedFromAssetId
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to ingest knowledge: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * List assets.
   */
  async listKnowledge(namespace = null) {
    const rawResult = await mcpClient.callTool("list_knowledge", {
      namespace
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to list knowledge: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Retrieve chunks.
   */
  async retrieveKnowledgePlatform(query, namespace = null, strategy = "hybrid", filters = {}, limit = 5, minScore = null, metadata = {}) {
    const rawResult = await mcpClient.callTool("retrieve_knowledge_platform", {
      query,
      namespace,
      strategy,
      filters,
      limit,
      min_score: minScore,
      metadata
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to retrieve from knowledge platform: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Update index.
   */
  async updateIndex(indexName, indexData) {
    const rawResult = await mcpClient.callTool("update_index", {
      index_name: indexName,
      index_data: indexData
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to update index: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Rebuild embeddings.
   */
  async rebuildEmbeddings(namespace) {
    const rawResult = await mcpClient.callTool("rebuild_embeddings", {
      namespace
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to rebuild embeddings: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Stats.
   */
  async knowledgeStatistics() {
    const rawResult = await mcpClient.callTool("knowledge_statistics", {});
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to get knowledge statistics: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  }
};
