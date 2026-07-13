import { mcpClient } from "./mcpClient.js";

export const intentClient = {
  /**
   * Domain client wrapper for intent classification.
   * @param {string} rawText - Raw content of the incoming message.
   * @param {string} source - Source channel of the message ("email", "form", "file_upload").
   * @param {string} senderEmail - Email address of the sender.
   * @param {Object} [context] - Execution trace mapping (event_id, job_id, trace_id).
   * @returns {Promise<{ intent: string, confidence: number, fallback_used: boolean, reasoning: string }>}
   */
  async classifyCandidateIntent(rawText, source, senderEmail, context = {}) {
    const rawResult = await mcpClient.callTool("classify_intent", {
      raw_text: rawText,
      source,
      sender_email: senderEmail,
      context
    });

    const parsed = JSON.parse(rawResult);

    // Schema validations and assertions to enforce core data contract
    if (
      typeof parsed.intent !== "string" ||
      typeof parsed.confidence !== "number" ||
      typeof parsed.fallback_used !== "boolean" ||
      typeof parsed.reasoning !== "string"
    ) {
      throw new Error("Invalid domain schema structure returned from classify_intent tool");
    }

    return {
      intent: parsed.intent,
      confidence: parsed.confidence,
      fallback_used: parsed.fallback_used,
      reasoning: parsed.reasoning
    };
  }
};
