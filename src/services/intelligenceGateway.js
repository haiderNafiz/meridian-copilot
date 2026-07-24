import { intentClient } from "./intentClient.js";
import { candidateClient } from "./candidateClient.js";
import { enrichmentClient } from "./enrichmentClient.js";
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
   * Facade method for candidate profiling.
   * Centralizes tracing context enrichment and delegates to candidateClient.
   * @param {string} rawText - Unstructured candidate profile or resume text.
   * @param {string|null} [currentTitle] - Candidate current title.
   * @param {string[]|null} [skills] - Candidate skills.
   * @param {number|null} [yearsExperience] - Candidate years of experience.
   * @param {Object|null} [jobContext] - Job description alignment context.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Profiling results object.
   */
  async profileCandidate(
    rawText,
    currentTitle = null,
    skills = null,
    yearsExperience = null,
    jobContext = null,
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing profileCandidate - TraceID: ${context.trace_id}`);

    return candidateClient.profileCandidate(rawText, currentTitle, skills, yearsExperience, jobContext, context);
  },

  /**
   * Facade method for deterministic enrichment.
   * @param {Object} params - Input fields.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Mapped result.
   */
  async enrichEntity(params = {}, jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing enrichEntity - TraceID: ${context.trace_id}`);

    return enrichmentClient.enrichEntity(params, context);
  },

  /**
   * Cleanup transport connection pool.
   */
  async close() {
    await mcpClient.close();
  }
};
