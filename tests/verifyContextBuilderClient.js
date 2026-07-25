import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function main() {
  console.log("Starting Node.js Context Builder E2E verification...");

  try {
    const contextId = "ctx_node_e2e_888";
    const documentReferences = ["doc_node_resume_1"];
    const sessionId = "session_node_1";
    const rawText = "Transient raw resume details";

    const candidateProfile = {
      role_type: "Backend",
      seniority: "Senior",
      urgency: "passive_looker",
      open_to_negotiation: true,
      management_level: "IC",
      predicted_functions: ["API Design"],
      technical_domains: ["Go"],
      confidence: 0.9,
      evidence: ["Experience matching Go"],
      reasoning: "Profile match"
    };

    const candidateEnrichment = {
      status: "success",
      metadata: {
        provider: "enricher",
        model: "n/a",
        prompt_version: "1.0.0",
        confidence: 1.0,
        fallback_used: false,
        provider_latency_ms: 0
      },
      payload: {
        technology_keywords: {
          normalized_value: ["go"],
          source: "rule_tech",
          confidence: 1.0,
          validation_status: "valid",
          evidence: ["Go matches"]
        },
        timezone: {
          normalized_value: "PST",
          source: "rule_tz",
          confidence: 1.0,
          validation_status: "valid",
          evidence: ["PST matches"]
        },
        country: {
          normalized_value: "US",
          source: "rule_country",
          confidence: 1.0,
          validation_status: "valid",
          evidence: ["US matches"]
        }
      }
    };

    const retrievedContext = [
      {
        text: "Requires Senior Go Developer",
        score: 0.92,
        metadata: {
          document_id: "jd_go",
          chunk_id: "jd_go_chunk_0",
          source: "jd.txt",
          chunk_index: 0
        }
      }
    ];

    const qualificationScores = {
      scores: {
        overall_qualification: {
          score: 0.88,
          reasoning: "Excellent Go fit",
          evidence: ["Proven history"],
          confidence: 0.88
        }
      },
      reconciliation_notes: "Perfect structural match."
    };

    const recruiterSummary = {
      summary_type: "candidate",
      executive_summary: "Strong candidate matching overall requirements.",
      strengths: {
        evidence: ["Highly skilled in Go"],
        reasoning: "Strong engineering background"
      },
      weaknesses_or_risks: {
        evidence: [],
        reasoning: ""
      },
      recruiter_recommendation: "Move to screen",
      interview_focus: ["Go concurrency"],
      follow_up_questions: ["Why channels?"]
    };

    const jobContextData = {
      event_id: "evt_builder_e2e_1",
      job_id: "job_builder_e2e_1",
      trace_id: "trace_builder_e2e_1"
    };

    console.log("Calling buildContext via Gateway...");
    const result = await intelligenceGateway.buildContext(
      contextId,
      documentReferences,
      sessionId,
      rawText,
      candidateProfile,
      candidateEnrichment,
      retrievedContext,
      qualificationScores,
      recruiterSummary,
      jobContextData
    );

    console.log("\n--- Context Builder Gateway Returned Result ---");
    console.log(JSON.stringify(result, null, 2));

    const payload = result.payload;
    if (
      result.status === "success" &&
      typeof payload === "object" &&
      payload.metadata.context_id === "ctx_node_e2e_888" &&
      payload.metadata.session_id === "session_node_1" &&
      payload.inputs.raw_text === "Transient raw resume details" &&
      payload.facts.role_type === "Backend" &&
      payload.facts.normalized_technologies.includes("go") &&
      payload.facts.timezone === "PST" &&
      payload.facts.country === "US" &&
      payload.evidence.profile_evidence.includes("Experience matching Go") &&
      payload.evidence.scoring_evidence.overall_qualification.includes("Proven history") &&
      payload.reasoning.summary_reasoning === "Strong candidate matching overall requirements." &&
      payload.outputs.qualification_scores.reconciliation_notes === "Perfect structural match."
    ) {
      console.log("\nSUCCESS: Context Builder compiled, structured, and validated successfully E2E!");
    } else {
      console.error("\nFAILURE: Schema verification checks on E2E Gateway snapshot output failed.");
      process.exitCode = 1;
    }

  } catch (error) {
    console.error("Context Builder verification failed with error:", error);
    process.exitCode = 1;
  } finally {
    await intelligenceGateway.close();
    console.log("Context Builder verification finished.");
  }
}

main().catch(console.error);
