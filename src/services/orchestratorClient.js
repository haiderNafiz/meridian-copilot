import { mcpClient } from "./mcpClient.js";

export const orchestratorClient = {
  /**
   * Domain client wrapper to run the agent orchestrator.
   * @param {string} queryText - Raw user message/query prompting action.
   * @param {string} [sessionId] - Optional session code.
   * @param {string} [contextId] - Optional preceding context ID.
   * @param {string[]} [forceTools] - Optional list of tools to enforce.
   * @param {string} [email] - Optional candidate email.
   * @param {string} [location] - Optional candidate location.
   * @param {string[]} [technologyKeywords] - Optional candidate tech keywords.
   * @param {Object} [context] - Trace markers.
   * @returns {Promise<Object>} Orchestration response.
   */
  async runOrchestration(
    queryText,
    sessionId = null,
    contextId = null,
    forceTools = [],
    email = null,
    location = null,
    technologyKeywords = [],
    context = {}
  ) {
    const rawResult = await mcpClient.callTool("run_orchestrator", {
      query_text: queryText,
      session_id: sessionId,
      context_id: contextId,
      force_tools: forceTools,
      email,
      location,
      technology_keywords: technologyKeywords,
      context
    });

    const parsed = JSON.parse(rawResult);
    if (typeof parsed.status !== "string" || typeof parsed.execution_trace_id !== "string") {
      throw new Error("Invalid domain schema structure returned from run_orchestrator tool");
    }
    return parsed;
  }
};
