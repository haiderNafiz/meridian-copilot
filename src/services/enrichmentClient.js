import { mcpClient } from "./mcpClient.js";

export const enrichmentClient = {
  /**
   * Domain client wrapper for deterministic entity enrichment.
   * @param {Object} params - Input fields to enrich.
   * @param {Object} [context] - Execution trace mapping (event_id, job_id, trace_id).
   * @returns {Promise<Object>} Enrichment result.
   */
  async enrichEntity(params = {}, context = {}) {
    const rawResult = await mcpClient.callTool("enrich_entity", {
      company_name: params.companyName || null,
      website: params.website || null,
      email: params.email || null,
      linkedin_url: params.linkedinUrl || null,
      github_url: params.githubUrl || null,
      phone_number: params.phoneNumber || null,
      country: params.country || null,
      location: params.location || null,
      technology_keywords: params.technologyKeywords || null,
      other_fields: params.otherFields || null,
      context
    });

    const parsed = JSON.parse(rawResult);

    if (
      typeof parsed.status !== "string" ||
      typeof parsed.metadata !== "object" ||
      typeof parsed.payload !== "object"
    ) {
      throw new Error("Invalid domain schema structure returned from enrich_entity tool");
    }

    return parsed;
  }
};
