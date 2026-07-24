import { mcpClient } from "./mcpClient.js";

export const candidateClient = {
  /**
   * Domain client wrapper for candidate profiling.
   * @param {string} rawText - Unstructured candidate profile or resume text.
   * @param {string|null} [currentTitle] - Candidate's current professional title.
   * @param {string[]|null} [skills] - Array of core candidate skills.
   * @param {number|null} [yearsExperience] - Years of candidate work experience.
   * @param {Object|null} [jobContext] - Job description/requirements to align profiling against.
   * @param {Object} [context] - Execution trace mapping (event_id, job_id, trace_id).
   * @returns {Promise<Object>} Mapped candidate profiling output.
   */
  async profileCandidate(
    rawText,
    currentTitle = null,
    skills = null,
    yearsExperience = null,
    jobContext = null,
    context = {}
  ) {
    const rawResult = await mcpClient.callTool("profile_candidate", {
      raw_text: rawText,
      current_title: currentTitle,
      skills,
      years_experience: yearsExperience,
      job_context: jobContext,
      context
    });

    const parsed = JSON.parse(rawResult);

    // Schema validations and assertions to enforce core data contract
    if (
      typeof parsed.role_type !== "string" ||
      typeof parsed.seniority !== "string" ||
      typeof parsed.urgency !== "string" ||
      typeof parsed.open_to_negotiation !== "boolean" ||
      !Array.isArray(parsed.predicted_functions) ||
      !Array.isArray(parsed.technical_domains) ||
      (parsed.management_level !== null && typeof parsed.management_level !== "string") ||
      !Array.isArray(parsed.evidence) ||
      typeof parsed.confidence !== "number" ||
      typeof parsed.reasoning !== "string"
    ) {
      throw new Error("Invalid domain schema structure returned from profile_candidate tool");
    }

    return {
      role_type: parsed.role_type,
      seniority: parsed.seniority,
      urgency: parsed.urgency,
      open_to_negotiation: parsed.open_to_negotiation,
      predicted_functions: parsed.predicted_functions,
      technical_domains: parsed.technical_domains,
      management_level: parsed.management_level,
      evidence: parsed.evidence,
      confidence: parsed.confidence,
      reasoning: parsed.reasoning
    };
  }
};
