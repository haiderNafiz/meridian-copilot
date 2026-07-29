import { intentClient } from "./intentClient.js";
import { candidateClient } from "./candidateClient.js";
import { enrichmentClient } from "./enrichmentClient.js";
import { retrievalClient } from "./retrievalClient.js";
import { qualificationClient } from "./qualificationClient.js";
import { summarizationClient } from "./summarizationClient.js";
import { contextBuilderClient } from "./contextBuilderClient.js";
import { memoryClient } from "./memoryClient.js";
import { orchestratorClient } from "./orchestratorClient.js";
import { plannerClient } from "./plannerClient.js";
import { conversationMemoryClient } from "./conversationMemoryClient.js";
import { opportunityIntelligenceClient } from "./opportunityIntelligenceClient.js";
import { revenueCopilotClient } from "./revenueCopilotClient.js";
import { evaluationClient } from "./evaluationClient.js";
import { replayClient } from "./replayClient.js";
import { feedbackClient } from "./feedbackClient.js";
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
   * Facade method for Knowledge Platform semantic retrieval.
   * @param {string} query - Search term.
   * @param {string} [collection] - Target namespace collection.
   * @param {number} [limit] - Max chunks to retrieve.
   * @param {number} [threshold] - Score cut-off filters.
   * @param {Object} [filters] - Metadata filters.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Retrieval output.
   */
  async retrieveKnowledge(
    query,
    collection = "default",
    limit = 5,
    threshold = 0.0,
    filters = null,
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing retrieveKnowledge - TraceID: ${context.trace_id}`);

    return retrievalClient.retrieveKnowledge(query, collection, limit, threshold, filters, context);
  },

  /**
   * Facade method for Qualification Scorer evaluation.
   * @param {string} rawText - Unstructured candidate description or resume content.
   * @param {string} jobDescriptionId - Target job description identifier.
   * @param {string} [email] - Candidate email identifier.
   * @param {string} [location] - Raw candidate location details.
   * @param {string[]} [technologyKeywords] - List of technologies.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Qualification output.
   */
  async scoreQualification(
    rawText,
    jobDescriptionId,
    email = null,
    location = null,
    technologyKeywords = null,
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing scoreQualification - TraceID: ${context.trace_id}`);

    return qualificationClient.scoreQualification(rawText, jobDescriptionId, email, location, technologyKeywords, context);
  },

  /**
   * Facade method for Candidate Summarizer evaluation.
   * @param {string} rawText - Unstructured candidate description or resume content.
   * @param {string} jobDescriptionId - Target job description identifier.
   * @param {string} [email] - Candidate email identifier.
   * @param {string} [location] - Raw candidate location details.
   * @param {string[]} [technologyKeywords] - List of technologies.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Summarization output.
   */
  async summarizeCandidate(
    rawText,
    jobDescriptionId,
    email = null,
    location = null,
    technologyKeywords = null,
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing summarizeCandidate - TraceID: ${context.trace_id}`);

    return summarizationClient.summarizeCandidate(rawText, jobDescriptionId, email, location, technologyKeywords, context);
  },

  /**
   * Facade method for Context Builder snapshot composition.
   * @param {string} contextId - Immutable snapshot context ID.
   * @param {string[]} documentReferences - References list.
   * @param {string} [sessionId] - Conversational session code.
   * @param {string} [rawText] - Optional transient text content.
   * @param {Object} [candidateProfile] - Extracted candidate profile.
   * @param {Object} [candidateEnrichment] - Deterministic enrichments.
   * @param {Object[]} [retrievedContext] - Vector DB chunks.
   * @param {Object} [qualificationScores] - Scorer scores.
   * @param {Object} [recruiterSummary] - Recruiter evaluation summary.
   * @param {Object} [jobContextData] - Session tracing values.
   * @returns {Promise<Object>} Composed ContextSnapshot.
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
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing buildContext - TraceID: ${context.trace_id}`);

    return contextBuilderClient.buildContext(
      contextId,
      documentReferences,
      sessionId,
      rawText,
      candidateProfile,
      candidateEnrichment,
      retrievedContext,
      qualificationScores,
      recruiterSummary,
      context
    );
  },

  /**
   * Facade method for saving or merging a ContextSnapshot to the Memory Service.
   */
  async saveMemory(snapshot, sessionId = null, tags = [], importance = 1.0, context = {}) {
    context.trace_id = context.trace_id || `tr_${Math.floor(Math.random() * 1000000)}`;
    console.log(`[Intelligence Gateway] Routing saveMemory - TraceID: ${context.trace_id}`);
    return memoryClient.saveMemory(snapshot, sessionId, tags, importance, context);
  },

  /**
   * Facade method for retrieving memories by identifiers.
   */
  async retrieveMemory(memoryId = null, contextId = null, sessionId = null, context = {}) {
    context.trace_id = context.trace_id || `tr_${Math.floor(Math.random() * 1000000)}`;
    console.log(`[Intelligence Gateway] Routing retrieveMemory - TraceID: ${context.trace_id}`);
    return memoryClient.retrieveMemory(memoryId, contextId, sessionId, context);
  },

  /**
   * Facade method for searching memories using query criteria.
   */
  async searchMemory(queryText = null, sessionId = null, tags = [], importanceThreshold = 0.0, limit = 10, context = {}) {
    context.trace_id = context.trace_id || `tr_${Math.floor(Math.random() * 1000000)}`;
    console.log(`[Intelligence Gateway] Routing searchMemory - TraceID: ${context.trace_id}`);
    return memoryClient.searchMemory(queryText, sessionId, tags, importanceThreshold, limit, context);
  },

  /**
   * Facade method for the Agent Orchestrator pipeline execution.
   */
  async runOrchestration(
    queryText,
    sessionId = null,
    contextId = null,
    forceTools = [],
    email = null,
    location = null,
    technologyKeywords = [],
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing runOrchestration - TraceID: ${context.trace_id}`);

    return orchestratorClient.runOrchestration(
      queryText,
      sessionId,
      contextId,
      forceTools,
      email,
      location,
      technologyKeywords,
      context
    );
  },

  /**
   * Facade method for running the planner service.
   * @param {string} queryText - Raw user query instruction.
   * @param {string} [sessionId] - Optional session code.
   * @param {string} [contextId] - Optional preceding context snapshot ID.
   * @param {string} [forceWorkflow] - Optional enforced workflow name.
   * @param {string} [email] - Optional candidate email.
   * @param {string} [location] - Optional candidate location.
   * @param {string[]} [technologyKeywords] - Optional technology keywords list.
   * @param {Object} [jobContextData] - Context map containing event_id, job_id, and trace_id.
   * @returns {Promise<Object>} Planning results response.
   */
  async runPlanner(
    queryText,
    sessionId = null,
    contextId = null,
    forceWorkflow = null,
    email = null,
    location = null,
    technologyKeywords = [],
    jobContextData = {}
  ) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing runPlanner - TraceID: ${context.trace_id}`);

    return plannerClient.runPlanner(
      queryText,
      sessionId,
      contextId,
      forceWorkflow,
      email,
      location,
      technologyKeywords,
      context
    );
  },

  /**
   * Facade method to post conversational turn.
   * @param {string} sessionId - Session ID.
   * @param {string} role - user or assistant.
   * @param {string} content - message text.
   * @param {string|null} [activeGoal] - active goal string.
   * @param {Object} [jobContextData] - Context markers.
   * @returns {Promise<Object>} Status result.
   */
  async postConversationTurn(sessionId, role, content, activeGoal = null, jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing postConversationTurn - TraceID: ${context.trace_id}`);

    return conversationMemoryClient.postConversationTurn(
      sessionId,
      role,
      content,
      activeGoal,
      context
    );
  },

  /**
   * Facade method to retrieve consolidated conversation context.
   * @param {string} sessionId - Session ID.
   * @param {string|null} [queryText] - Search query.
   * @param {string|null} [activeGoal] - active goal override.
   * @param {Object} [jobContextData] - Context markers.
   * @returns {Promise<Object>} Consolidated context.
   */
  async getConversationContext(sessionId, queryText = null, activeGoal = null, jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing getConversationContext - TraceID: ${context.trace_id}`);

    return conversationMemoryClient.getConversationContext(
      sessionId,
      queryText,
      activeGoal,
      context
    );
  },

  /**
   * Facade method to evaluate opportunities with opportunity intelligence tool.
   * @param {Object} contextSnapshot - context builder output payload.
   * @param {Object|null} [conversationContext] - dialog memory context.
   * @param {string} [assessmentType] - target strategy type enum.
   * @param {Object} [jobContextData] - Context markers.
   * @returns {Promise<Object>} Mapped assessment result.
   */
  async assessOpportunity(contextSnapshot, conversationContext = null, assessmentType = "candidate", jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing assessOpportunity - TraceID: ${context.trace_id}`);

    return opportunityIntelligenceClient.assessOpportunity(
      contextSnapshot,
      conversationContext,
      assessmentType,
      context
    );
  },

  /**
   * Facade method to generate playbooks and recommendations via revenue copilot.
   * @param {Object} opportunityAssessment - Preceding opportunity evaluation.
   * @param {Object} contextSnapshot - Context snapshot data.
   * @param {Object|null} [conversationContext] - Optional memory context.
   * @param {Object} [jobContextData] - Tracing context metrics.
   * @returns {Promise<Object>} Mapped copilot recommendation.
   */
  async runRevenueCopilot(opportunityAssessment, contextSnapshot, conversationContext = null, jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing runRevenueCopilot - TraceID: ${context.trace_id}`);

    return revenueCopilotClient.runRevenueCopilot(
      opportunityAssessment,
      contextSnapshot,
      conversationContext,
      context
    );
  },

  /**
   * Facade method to run evaluations.
   * @param {string} domain - Mapped dataset domain.
   * @param {string} datasetType - Golden/Synthetic/Regression datasets tag.
   * @param {string} version - Dataset version identifier.
   * @param {Object} config - Config metrics specifications.
   * @param {string} [experimentId] - Experiment group.
   * @param {Object} [jobContextData] - Custom context identifiers.
   * @returns {Promise<Object>} The resolved EvaluationResult.
   */
  async runEvaluation(domain, datasetType, version, config, experimentId = "exp_default", jobContextData = {}) {
    const context = {
      event_id: jobContextData.event_id || `evt_${Math.random().toString(36).substring(2, 11)}`,
      job_id: jobContextData.job_id || "direct_call",
      trace_id: jobContextData.trace_id || jobContextData.job_id || `trace_${Math.random().toString(36).substring(2, 11)}`
    };

    console.log(`[Intelligence Gateway] Routing runEvaluation - TraceID: ${context.trace_id}`);

    return evaluationClient.runEvaluation(
      domain,
      datasetType,
      version,
      config,
      experimentId,
      context
    );
  },

  /**
   * Facade method to manually create a replay session.
   */
  async createReplay(targetId, inputPayload, outputPayload, parentReplayId = null, metadata = {}) {
    console.log(`[Intelligence Gateway] Routing createReplay for Target: ${targetId}`);
    return replayClient.createReplay(targetId, inputPayload, outputPayload, parentReplayId, metadata);
  },

  /**
   * Facade method to run a replay.
   */
  async replayExecution(replayId, overrideConfig = null) {
    console.log(`[Intelligence Gateway] Routing replayExecution - ReplayID: ${replayId}`);
    return replayClient.replayExecution(replayId, overrideConfig);
  },

  /**
   * Facade method to compare replayed runs.
   */
  async compareReplays(replayId, overrideConfig = null) {
    console.log(`[Intelligence Gateway] Routing compareReplays - ReplayID: ${replayId}`);
    return replayClient.compareReplays(replayId, overrideConfig);
  },

  /**
   * Facade method to generate debug report.
   */
  async generateDebugReport(replayId, overrideConfig = null, format = "json") {
    console.log(`[Intelligence Gateway] Routing generateDebugReport - ReplayID: ${replayId} Format: ${format}`);
    return replayClient.generateDebugReport(replayId, overrideConfig, format);
  },

  /**
   * Facade method to submit feedback.
   */
  async submitFeedback(targetId, targetType, runId, feedbackType, feedbackPayload, reviewerId = null, replayId = null, evaluationId = null, metadata = {}) {
    console.log(`[Intelligence Gateway] Routing submitFeedback for Target: ${targetId}`);
    return feedbackClient.submitFeedback(targetId, targetType, runId, feedbackType, feedbackPayload, reviewerId, replayId, evaluationId, metadata);
  },

  /**
   * Facade method to list feedback.
   */
  async listFeedback(targetId = null, runId = null) {
    console.log(`[Intelligence Gateway] Routing listFeedback - TargetID: ${targetId}`);
    return feedbackClient.listFeedback(targetId, runId);
  },

  /**
   * Facade method to retrieve feedback record.
   */
  async getFeedback(feedbackId) {
    console.log(`[Intelligence Gateway] Routing getFeedback - FeedbackID: ${feedbackId}`);
    return feedbackClient.getFeedback(feedbackId);
  },

  /**
   * Facade method to compute feedback summary/analytics.
   */
  async feedbackSummary(targetId) {
    console.log(`[Intelligence Gateway] Routing feedbackSummary - TargetID: ${targetId}`);
    return feedbackClient.feedbackSummary(targetId);
  },

  /**
   * Facade method to promote target replay item.
   */
  async promoteDatasetItem(replayId, targetDomain, targetDatasetType, targetVersion, actor) {
    console.log(`[Intelligence Gateway] Routing promoteDatasetItem for Replay: ${replayId}`);
    return feedbackClient.promoteDatasetItem(replayId, targetDomain, targetDatasetType, targetVersion, actor);
  },

  /**
   * Cleanup transport connection pool.
   */
  async close() {
    await mcpClient.close();
  }
};
