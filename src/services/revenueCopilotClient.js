import { mcpClient } from "./mcpClient.js";

export const revenueCopilotClient = {
  /**
   * Run revenue copilot to generate playbook recommendations, checklists, and draft communication.
   * @param {Object} opportunityAssessment - Preceding opportunity assessment.
   * @param {Object} contextSnapshot - Context snapshot data.
   * @param {Object|null} [conversationContext] - Optional conversation context history.
   * @param {Object} [context] - Tracing context data.
   * @returns {Promise<Object>} The copilot recommendation result.
   */
  async runRevenueCopilot(opportunityAssessment, contextSnapshot, conversationContext = null, context = {}) {
    const rawResult = await mcpClient.callTool("run_revenue_copilot", {
      opportunity_assessment: opportunityAssessment,
      context_snapshot: contextSnapshot,
      conversation_context: conversationContext,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !parsed.recommendation) {
      throw new Error("Invalid domain schema structure returned from run_revenue_copilot tool");
    }
    return parsed;
  }
};
