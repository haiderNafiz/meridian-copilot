import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Revenue Copilot...");

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

    const dummyAssessment = {
      assessment_type: "candidate",
      business_intent: "Vetting query",
      lifecycle_stage: "Discovery",
      confidence: 0.8,
      opportunity_score: 0.85,
      strengths: ["Strong skills"],
      risks: [],
      blockers: [],
      missing_information: [],
      evidence_summary: {},
      recommended_next_actions: ["REQUIRED: Obtain email"],
      recommended_plan: "candidate_screening",
      follow_up_items: [],
      decision_guidance: "Standard vetting screen",
      explanation: "No issues found",
      telemetry: {}
    };

    const dummyConversationContext = {
      session_id: "s4_node",
      active_goal: "assess_candidate",
      turns: [],
      active_entities: {},
      pending_actions: [],
      unresolved_questions: ["Is he open to remote?"]
    };

    console.log("1. Calling runRevenueCopilot facade via intelligence gateway...");
    const result = await intelligenceGateway.runRevenueCopilot(
      dummyAssessment,
      dummySnapshot,
      dummyConversationContext
    );

    console.log("Revenue Copilot Gateway Success Response:");
    console.log(JSON.stringify(result, null, 2));

    if (result.status !== "success") {
      throw new Error(`Expected status 'success', got '${result.status}'`);
    }

    const rec = result.recommendation;
    if (!rec) {
      throw new Error("recommendation field is missing in response");
    }

    if (rec.playbook.category !== "evaluation") {
      throw new Error(`Expected category 'evaluation', got '${rec.playbook.category}'`);
    }

    if (rec.playbook.playbook_name !== "candidate_screening") {
      throw new Error(`Expected playbook_name 'candidate_screening', got '${rec.playbook.playbook_name}'`);
    }

    if (rec.drafts.length !== 4) {
      throw new Error(`Expected 4 generated drafts, got ${rec.drafts.length}`);
    }

    console.log("Node.js Revenue Copilot E2E Verification PASSED successfully!");
  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    await intelligenceGateway.close();
  }
}

run();
