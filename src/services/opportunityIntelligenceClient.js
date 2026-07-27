import { mcpClient } from "./mcpClient.js";

export const opportunityIntelligenceClient = {
  /**
   * Assess opportunity based on snapshot and conversation contexts.
   * @param {Object} contextSnapshot - Context snapshot data.
   * @param {Object|null} [conversationContext] - Optional conversation context history.
   * @param {string} [assessmentType] - AssessmentType value (e.g. "candidate").
   * @param {Object} [context] - Tracing context data.
   * @returns {Promise<Object>} The resolved OpportunityAssessment.
   */
  async assessOpportunity(contextSnapshot, conversationContext = null, assessmentType = "candidate", context = {}) {
    const rawResult = await mcpClient.callTool("assess_opportunity", {
      context_snapshot: contextSnapshot,
      conversation_context: conversationContext,
      assessment_type: assessmentType,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || !parsed.assessment) {
      throw new Error("Invalid domain schema structure returned from assess_opportunity tool");
    }
    return parsed;
  }
};
