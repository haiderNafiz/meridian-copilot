import { mcpClient } from "./mcpClient.js";

export const replayClient = {
  /**
   * Manually record a target execution input/output payload for debugging.
   */
  async createReplay(targetId, inputPayload, outputPayload, parentReplayId = null, metadata = {}) {
    const rawResult = await mcpClient.callTool("create_replay", {
      target_id: targetId,
      input_payload: inputPayload,
      output_payload: outputPayload,
      parent_replay_id: parentReplayId,
      metadata
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to create replay: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Replay execution by recorded execution ID.
   */
  async replayExecution(replayId, overrideConfig = null) {
    const rawResult = await mcpClient.callTool("replay_execution", {
      replay_id: replayId,
      override_config: overrideConfig
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to replay execution: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Compare original execution against replayed execution.
   */
  async compareReplays(replayId, overrideConfig = null) {
    const rawResult = await mcpClient.callTool("compare_replays", {
      replay_id: replayId,
      override_config: overrideConfig
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to compare replays: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  },

  /**
   * Generate debug report.
   */
  async generateDebugReport(replayId, overrideConfig = null, format = "json") {
    const rawResult = await mcpClient.callTool("generate_debug_report", {
      replay_id: replayId,
      override_config: overrideConfig,
      format
    });
    const parsed = JSON.parse(rawResult);
    if (parsed.status !== "success") {
      throw new Error(`Failed to generate debug report: ${parsed.error || "unknown error"}`);
    }
    return parsed;
  }
};
