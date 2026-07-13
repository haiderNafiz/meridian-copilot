import { intentClient } from "./intentClient.js";
import { mcpClient } from "./mcpClient.js";

export const intelligenceGateway = {
  /**
   * Facade method for candidate intent classification.
   * Centralizes tracing context enrichment and delegates to intentClient.
   * @param {string} rawText - Message content.
   * @param {string} source - Message source.
   * @param {string} senderEmail - Sender email.
   * @param {Object} [jobContext] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<{ intent: string, confidence: number, fallback_used: boolean, reasoning: string }>}
   */
  async classifyCandidateIntent(rawText, source, senderEmail, jobContext = {}) {
    // Enrich context with unique request mapping if not present
    const context = {
      event_id: jobContext.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContext.job_id || "direct_call",
      trace_id: jobContext.trace_id || jobContext.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing classifyCandidateIntent - TraceID: ${context.trace_id}`);

    return intentClient.classifyCandidateIntent(rawText, source, senderEmail, context);
  },

  /**
   * Cleanup transport connection pool.
   */
  async close() {
    await mcpClient.close();
  }
};
