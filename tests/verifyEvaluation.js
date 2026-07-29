import fs from "fs";
import path from "path";
import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Evaluation Framework...");

  // 1. Setup mock datasets structure
  const datasetsDir = path.resolve("datasets/intent/golden");
  fs.mkdirSync(datasetsDir, { recursive: true });
  
  const sampleDataset = {
    dataset_id: "intent_golden",
    version: "v1",
    dataset_type: "golden",
    items: [
      {
        id: "item1",
        input_payload: { raw_text: "hello" },
        expected_output: { result: "mocked", tool: "evaluation_default", input: { raw_text: "hello" } },
        tags: ["test"],
        metadata: {}
      }
    ]
  };
  
  const datasetPath = path.join(datasetsDir, "v1.json");
  fs.writeFileSync(datasetPath, JSON.stringify(sampleDataset, null, 2), "utf-8");

  try {
    const config = {
      target_id: "evaluation_default",
      metrics: ["classification"],
      thresholds: { classification: 0.8 }
    };

    console.log("1. Calling runEvaluation facade via intelligence gateway...");
    const result = await intelligenceGateway.runEvaluation(
      "intent",
      "golden",
      "v1",
      config,
      "exp_node_test"
    );

    console.log("Evaluation Gateway Success Response:");
    console.log(JSON.stringify(result, null, 2));

    if (result.status !== "success") {
      throw new Error(`Expected status 'success', got '${result.status}'`);
    }

    const report = result.report;
    if (!report) {
      throw new Error("Report field is missing in response");
    }

    if (report.overall_score !== 1.0) {
      throw new Error(`Expected overall_score 1.0, got ${report.overall_score}`);
    }

    console.log("Node.js Evaluation Framework E2E Verification PASSED successfully!");
  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    // Cleanup
    try {
      if (fs.existsSync(datasetPath)) {
        fs.unlinkSync(datasetPath);
      }
    } catch (e) {}
    await intelligenceGateway.close();
  }
}

run();
