import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Opportunity Intelligence...");

  try {
    const dummySnapshot = {
      metadata: {
        context_id: "c4_node",
        session_id: "s4_node",
        timestamp_utc: new Date().toISOString(),
        provenance: ["CandidateProfilerService", "DeterministicEnrichmentService"],
        overall_confidence: 1.0
      },
      inputs: {
        document_references: [],
        raw_text: "python backend dev"
      },
      facts: {
        role_type: "Backend",
        seniority: "Senior",
        normalized_technologies: ["python"],
        timezone: "UTC+1"
      },
      evidence: {
        profile_evidence: [],
        scoring_evidence: {}
      },
      reasoning: {
        scoring_reasoning: {},
        summary_reasoning: null,
        weaknesses_or_risks: null
      },
      outputs: {
        qualification_scores: null,
        recruiter_summary: null
      }
    };

    const dummyConversationContext = {
      session_id: "s4_node",
      active_goal: "assess_candidate",
      turns: [],
      active_entities: {},
      pending_actions: [],
      unresolved_questions: ["Is he open to remote?"]
    };

    console.log("1. Calling assessOpportunity facade via intelligence gateway...");
    const result = await intelligenceGateway.assessOpportunity(
      dummySnapshot,
      dummyConversationContext,
      "candidate"
    );

    console.log("Assess Opportunity Gateway Success Response:");
    console.log(JSON.stringify(result, null, 2));

    if (result.status !== "success") {
      throw new Error(`Expected status 'success', got '${result.status}'`);
    }

    const assessment = result.assessment;
    if (!assessment) {
      throw new Error("Assessment field is missing in response");
    }

    if (assessment.assessment_type !== "candidate") {
      throw new Error(`Expected assessment_type 'candidate', got '${assessment.assessment_type}'`);
    }

    if (typeof assessment.confidence !== "number" || assessment.confidence <= 0.0) {
      throw new Error(`Invalid confidence score: ${assessment.confidence}`);
    }

    if (assessment.recommended_plan !== "candidate_screening") {
      throw new Error(`Expected recommended_plan 'candidate_screening', got '${assessment.recommended_plan}'`);
    }

    console.log("Node.js Opportunity Intelligence E2E Verification PASSED successfully!");
  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

run();
