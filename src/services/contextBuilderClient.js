import { mcpClient } from "./mcpClient.js";

export const contextBuilderClient = {
  /**
   * Domain client wrapper for Context Builder tool.
   * @param {string} contextId - Immutable context snapshot tracking ID.
   * @param {string[]} documentReferences - Source resume/JD references.
   * @param {string} [sessionId] - Conversational session code.
   * @param {string} [rawText] - Optional transient raw candidate text.
   * @param {Object} [candidateProfile] - Profile output payload from CandidateProfilerService.
   * @param {Object} [candidateEnrichment] - Enrichment output payload from DeterministicEnrichmentService.
   * @param {Object[]} [retrievedContext] - Chunks array from Knowledge Platform.
   * @param {Object} [qualificationScores] - Scores payload from QualificationScorerService.
   * @param {Object} [recruiterSummary] - Summary payload from SummarizationService.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} The ContextSnapshot output.
   */
  async buildContext(
    contextId,
    documentReferences,
    sessionId = null,
    rawText = null,
    candidateProfile = null,
    candidateEnrichment = null,
    retrievedContext = null,
    qualificationScores = null,
    recruiterSummary = null,
    context = {}
  ) {
    const rawResult = await mcpClient.callTool("build_context", {
      context_id: contextId,
      document_references: documentReferences,
      session_id: sessionId,
      raw_text: rawText,
      candidate_profile: candidateProfile,
      candidate_enrichment: candidateEnrichment,
      retrieved_context: retrievedContext,
      qualification_scores: qualificationScores,
      recruiter_summary: recruiterSummary,
      context
    });

    const parsed = JSON.parse(rawResult);

    if (
      typeof parsed.status !== "string" ||
      typeof parsed.metadata !== "object" ||
      typeof parsed.payload !== "object"
    ) {
      throw new Error("Invalid domain schema structure returned from build_context tool");
    }

    return parsed;
  }
};
