import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Deterministic Enrichment verification...");

  try {
    const params = {
      companyName: "Stripe Inc.",
      website: "stripe.com",
      email: "recruiter@stripe.com",
      linkedinUrl: "https://www.linkedin.com/in/collison/",
      githubUrl: "colli",
      phoneNumber: "+1 (555) 019-3388",
      country: "USA",
      location: "San Francisco, CA",
      technologyKeywords: ["js", "React.js", "docker"]
    };

    const jobContextData = {
      event_id: "evt_enrichment_e2e_1",
      job_id: "job_enrichment_e2e_1",
      trace_id: "trace_enrichment_e2e_1"
    };

    console.log("Calling enrichEntity via Gateway...");
    const result = await intelligenceGateway.enrichEntity(params, jobContextData);

    console.log("\n--- Enrichment Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    const payload = result.payload;
    if (
      result.status === "success" &&
      result.metadata.provider === "deterministic" &&
      result.metadata.model === "rule-engine-v1" &&
      payload.company_name.normalized_value === "Stripe" &&
      payload.company_domain.normalized_value === "stripe.com" &&
      payload.timezone.normalized_value === "America/Los_Angeles" &&
      payload.phone_number.normalized_value === "+15550193388" &&
      payload.country.normalized_value === "United States" &&
      Array.isArray(payload.technology_keywords.normalized_value) &&
      payload.technology_keywords.normalized_value.includes("React")
    ) {
      console.log("\nSUCCESS: Deterministic enrichment executed, parsed, and validated successfully!");
    } else {
      console.error("\nFAILURE: Schema validation checks on Gateway result failed.");
    }

  } catch (error) {
    console.error("Deterministic enrichment verification failed with error:", error);
  } finally {
    await intelligenceGateway.close();
    console.log("Deterministic enrichment verification finished.");
  }
}

main().catch(console.error);
