import { mcpClient } from "./mcpClient.js";

export const memoryClient = {
  /**
   * Domain client wrapper to save/merge a ContextSnapshot.
   * @param {Object} snapshot - ContextSnapshot payload.
   * @param {string} [sessionId] - Session grouping tag.
   * @param {string[]} [tags] - Keyword tags.
   * @param {number} [importance] - Importance rating.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Persisted status response.
   */
  async saveMemory(snapshot, sessionId = null, tags = [], importance = 1.0, context = {}) {
    const rawResult = await mcpClient.callTool("save_memory", {
      snapshot,
      session_id: sessionId,
      tags,
      importance,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || typeof parsed.memory_id !== "string") {
      throw new Error("Invalid domain schema structure returned from save_memory tool");
    }
    return parsed;
  },

  /**
   * Domain client wrapper to retrieve a Memory snapshot.
   * @param {string} [memoryId] - Target memory identifier.
   * @param {string} [contextId] - Original context ID.
   * @param {string} [sessionId] - Session ID.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Retreival response.
   */
  async retrieveMemory(memoryId = null, contextId = null, sessionId = null, context = {}) {
    const rawResult = await mcpClient.callTool("retrieve_memory", {
      memory_id: memoryId,
      context_id: contextId,
      session_id: sessionId,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !Array.isArray(parsed.memories)) {
      throw new Error("Invalid domain schema structure returned from retrieve_memory tool");
    }
    return parsed;
  },

  /**
   * Domain client wrapper to search memories.
   * @param {string} [queryText] - Search string.
   * @param {string} [sessionId] - Filter session ID.
   * @param {string[]} [tags] - Filter tags.
   * @param {number} [importanceThreshold] - Minimum score.
   * @param {number} [limit] - Max matching records.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Search response.
   */
  async searchMemory(queryText = null, sessionId = null, tags = [], importanceThreshold = 0.0, limit = 10, context = {}) {
    const rawResult = await mcpClient.callTool("search_memory", {
      query_text: queryText,
      session_id: sessionId,
      tags,
      importance_threshold: importanceThreshold,
      limit,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !Array.isArray(parsed.results)) {
      throw new Error("Invalid domain schema structure returned from search_memory tool");
    }
    return parsed;
  }
};
