import { mcpClient } from "./mcpClient.js";

export const conversationMemoryClient = {
  /**
   * Post conversational turn to working memory.
   * @param {string} sessionId - Session ID.
   * @param {string} role - user, assistant, system.
   * @param {string} content - Message body.
   * @param {string|null} [activeGoal] - Active goal string.
   * @param {Object} [context] - Tracing context.
   * @returns {Promise<Object>} Response status result.
   */
  async postConversationTurn(sessionId, role, content, activeGoal = null, context = {}) {
    const rawResult = await mcpClient.callTool("post_conversation_turn", {
      session_id: sessionId,
      role,
      content,
      active_goal: activeGoal,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string") {
      throw new Error("Invalid domain schema structure returned from post_conversation_turn tool");
    }
    return parsed;
  },

  /**
   * Retrieve consolidated conversation context window.
   * @param {string} sessionId - Session ID.
   * @param {string|null} [queryText] - Search query keywords.
   * @param {string|null} [activeGoal] - Active goal override.
   * @param {Object} [context] - Tracing context.
   * @returns {Promise<Object>} Resolved context.
   */
  async getConversationContext(sessionId, queryText = null, activeGoal = null, context = {}) {
    const rawResult = await mcpClient.callTool("get_conversation_context", {
      session_id: sessionId,
      query_text: queryText,
      active_goal: activeGoal,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !parsed.context) {
      throw new Error("Invalid domain schema structure returned from get_conversation_context tool");
    }
    return parsed;
  }
};
