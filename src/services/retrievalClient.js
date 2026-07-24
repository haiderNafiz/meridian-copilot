import { mcpClient } from "./mcpClient.js";

export const retrievalClient = {
  /**
   * Domain client wrapper for Knowledge Platform semantic retrieval.
   * @param {string} query - Search term.
   * @param {string} [collection] - Target namespace collection.
   * @param {number} [limit] - Max chunks to retrieve.
   * @param {number} [threshold] - Score cut-off filters.
   * @param {Object} [filters] - Metadata filters.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Retrieval output.
   */
  async retrieveKnowledge(query, collection = "default", limit = 5, threshold = 0.0, filters = null, context = {}) {
    const rawResult = await mcpClient.callTool("retrieve_knowledge", {
      query,
      collection,
      limit,
      threshold,
      filters,
      context
    });

    const parsed = JSON.parse(rawResult);

    if (
      typeof parsed.status !== "string" ||
      typeof parsed.metadata !== "object" ||
      typeof parsed.payload !== "object"
    ) {
      throw new Error("Invalid domain schema structure returned from retrieve_knowledge tool");
    }

    return parsed;
  }
};
