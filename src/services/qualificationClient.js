import { mcpClient } from "./mcpClient.js";

export const qualificationClient = {
  /**
   * Domain client wrapper for Qualification Scorer tool.
   * @param {string} rawText - Unstructured candidate description or resume content.
   * @param {string} jobDescriptionId - Target job description identifier.
   * @param {string} [email] - Candidate email identifier.
   * @param {string} [location] - Raw candidate location details.
   * @param {string[]} [technologyKeywords] - List of technologies.
   * @param {Object} [context] - Execution tracing markers.
   * @returns {Promise<Object>} Qualification output.
   */
  async scoreQualification(rawText, jobDescriptionId, email = null, location = null, technologyKeywords = null, context = {}) {
    const rawResult = await mcpClient.callTool("score_qualification", {
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
      throw new Error("Invalid domain schema structure returned from score_qualification tool");
    }

    return parsed;
  }
};
