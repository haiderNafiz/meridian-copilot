import { mcpClient } from "./mcpClient.js";

export const summarizationClient = {
  /**
   * Domain client wrapper for Candidate Summarizer tool.
   * @param {string} rawText - Unstructured candidate description or resume content.
   * @param {string} jobDescriptionId - Target job description identifier.
   * @param {string} [email] - Candidate email identifier.
   * @param {string} [location] - Raw candidate location details.
   * @param {string[]} [technologyKeywords] - List of technologies.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Summarization output.
   */
  async summarizeCandidate(rawText, jobDescriptionId, email = null, location = null, technologyKeywords = null, context = {}) {
    const rawResult = await mcpClient.callTool("summarize_candidate", {
      raw_text: rawText,
      job_description_id: jobDescriptionId,
      email,
      location,
      technology_keywords: technologyKeywords,
      context
    });

    const parsed = JSON.parse(rawResult);

    if (
      typeof parsed.status !== "string" ||
      typeof parsed.metadata !== "object" ||
      typeof parsed.payload !== "object"
    ) {
      throw new Error("Invalid domain schema structure returned from summarize_candidate tool");
    }

    return parsed;
  }
};
