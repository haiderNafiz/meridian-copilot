import { mcpClient } from "./mcpClient.js";

export const plannerClient = {
  /**
   * Domain client wrapper to run the agent planner.
   * @param {string} queryText - Raw user message/query prompting planning.
   * @param {string} [sessionId] - Optional session code.
   * @param {string} [contextId] - Optional preceding context ID.
   * @param {string} [forceWorkflow] - Enforced workflow template name bypass.
   * @param {string} [email] - Optional candidate email override.
   * @param {string} [location] - Optional candidate location override.
   * @param {string[]} [technologyKeywords] - Optional candidate tech keywords.
   * @param {Object} [context] - Trace markers.
   * @returns {Promise<Object>} Planning response.
   */
  async runPlanner(
    queryText,
    sessionId = null,
    contextId = null,
    forceWorkflow = null,
    email = null,
    location = null,
    technologyKeywords = [],
    context = {}
  ) {
    const rawResult = await mcpClient.callTool("run_planner", {
      query_text: queryText,
      session_id: sessionId,
      context_id: contextId,
      force_workflow: forceWorkflow,
      email,
      location,
      technology_keywords: technologyKeywords,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string") {
      throw new Error("Invalid domain schema structure returned from run_planner tool");
    }
    return parsed;
  }
};
