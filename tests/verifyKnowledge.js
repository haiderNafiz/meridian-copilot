import fs from "fs";
import path from "path";
import { intelligenceGateway } from "../src/services/intelligenceGateway.js";

async function run() {
  console.log("Starting E2E Node.js verification for Production Knowledge Platform...");

  try {
    console.log("1. Ingesting knowledge asset via gateway...");
    const ingestRes = await intelligenceGateway.ingestKnowledge(
      "finance_node",
      "revenue projections.\n\nquarterly budgets.",
      "document",
      "proj_node_1",
      { visibility: "internal" }
    );

    console.log("Ingest Response:");
    console.log(JSON.stringify(ingestRes, null, 2));

    if (ingestRes.status !== "success" || !ingestRes.asset) {
      throw new Error("Invalid response when ingesting knowledge");
    }

    console.log("2. Querying knowledge assets...");
    const listRes = await intelligenceGateway.listKnowledge("finance_node");
    console.log("List Response:");
    console.log(JSON.stringify(listRes, null, 2));

    if (listRes.status !== "success" || !listRes.assets || listRes.assets.length === 0) {
      throw new Error("Invalid response when listing knowledge");
    }

    console.log("3. Retrieving chunks via query...");
    const retrieveRes = await intelligenceGateway.retrieveKnowledgePlatform(
      "revenue projections",
      "finance_node",
      "sparse",
      { visibility: "internal" },
      1
    );
    console.log("Retrieve Response:");
    console.log(JSON.stringify(retrieveRes, null, 2));

    if (retrieveRes.status !== "success" || !retrieveRes.chunks || retrieveRes.chunks.length === 0) {
      throw new Error("Invalid response when retrieving knowledge");
    }

    console.log("4. Fetching knowledge statistics...");
    const statsRes = await intelligenceGateway.knowledgeStatistics();
    console.log("Statistics Response:");
    console.log(JSON.stringify(statsRes, null, 2));

    if (statsRes.status !== "success" || !statsRes.analytics_summary) {
      throw new Error("Invalid response when fetching knowledge platform statistics");
    }

    console.log("Node.js Production Knowledge Platform E2E Verification PASSED successfully!");

  } catch (err) {
    console.error("Node.js E2E Verification FAILED:", err);
    process.exit(1);
  } finally {
    const kpDir = path.resolve("knowledge_platform");
    try {
      if (fs.existsSync(path.join(kpDir, "assets", "proj_node_1_v1.json"))) {
        fs.unlinkSync(path.join(kpDir, "assets", "proj_node_1_v1.json"));
      }
    } catch (e) {}
    await intelligenceGateway.close();
  }
}

run();
