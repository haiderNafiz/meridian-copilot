import { mcpClient } from "./mcpClient.js";

export const feedbackClient = {
  /**
   * Submit human or system feedback.
   */
  async submitFeedback(targetId, targetType, runId, feedbackType, feedbackPayload, reviewerId = null, replayId = null, evaluationId = null, metadata = {}) {
    const rawResult = await mcpClient.callTool("submit_feedback", {
      target_id: targetId,
      target_type: targetType,
      run_id: runId,
      feedback_type: feedbackType,
      feedback_payload: feedbackPayload,
      reviewer_id: reviewerId,
      replay_id: replayId,
      evaluation_id: evaluationId,
      metadata
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to submit feedback: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * List feedback records matching target/run filters.
   */
  async listFeedback(targetId = null, runId = null) {
    const rawResult = await mcpClient.callTool("list_feedback", {
      target_id: targetId,
      run_id: runId
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to list feedback: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Retrieve a specific feedback record.
   */
  async getFeedback(feedbackId) {
    const rawResult = await mcpClient.callTool("get_feedback", {
      feedback_id: feedbackId
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to get feedback: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Compute feedback summary.
   */
  async feedbackSummary(targetId) {
    const rawResult = await mcpClient.callTool("feedback_summary", {
      target_id: targetId
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to get feedback summary: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Promote high-quality reviewed replays to versioned immutable datasets.
   */
  async promoteDatasetItem(replayId, targetDomain, targetDatasetType, targetVersion, actor) {
    const rawResult = await mcpClient.callTool("promote_dataset_item", {
      replay_id: replayId,
      target_domain: targetDomain,
      target_dataset_type: targetDatasetType,
      target_version: targetVersion,
      actor
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to promote dataset item: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  }
};
