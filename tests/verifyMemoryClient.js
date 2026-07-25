import { intelligenceGateway } from "../src/services/intelligenceGateway.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function run() {
  console.log("Starting E2E Node.js verification for Memory Service...");

  // Setup sample context snapshot
  const snapshotV1 = {
    metadata: {
      context_id: "ctx_node_e2e_99",
      timestamp_utc: new Date().toISOString(),
      provenance: ["CandidateProfilerService"],
      overall_confidence: 0.92
    },
    inputs: {
      document_references: ["doc_ref_a"],
      raw_text: "Node developer with react experience."
    },
    facts: {
      role_type: "Full Stack",
      technical_domains: ["Node.js"],
      normalized_technologies: ["javascript"],
      timezone: "GMT+6",
      country: "BD"
    },
    evidence: {
      profile_evidence: ["Has 5 years react experience"],
      scoring_evidence: {}
    },
    reasoning: {
      scoring_reasoning: {},
      summary_reasoning: "Good developer match."
    },
    outputs: {}
  };

  try {
    // 1. Save V1 snapshot
    console.log("Saving V1 Snapshot...");
    const resSave1 = await intelligenceGateway.saveMemory(
      snapshotV1,
      "session_node_e2e_99",
      ["javascript", "react"],
      0.85
    );

    console.log("V1 Save success:", JSON.stringify(resSave1, null, 2));
    const memoryIdV1 = resSave1.memory_id;

    // 2. Save V2 snapshot (append update)
    const snapshotV2 = {
      metadata: {
        context_id: "ctx_node_e2e_99",
        timestamp_utc: new Date().toISOString(),
        provenance: ["CandidateProfilerService", "QualificationScorerService"],
        overall_confidence: 0.95
      },
      inputs: {
        document_references: ["doc_ref_a", "doc_ref_b"]
      },
      facts: {
        technical_domains: ["AWS"],
        normalized_technologies: ["aws"]
      },
      evidence: {
        profile_evidence: ["AWS certified Architect"]
      },
      reasoning: {
        summary_reasoning: "Experienced with AWS and Node"
      },
      outputs: {}
    };

    console.log("Saving V2 Snapshot (Append)...");
    const resSave2 = await intelligenceGateway.saveMemory(
      snapshotV2,
      "session_node_e2e_99",
      ["aws"],
      0.90
    );

    console.log("V2 Save success:", JSON.stringify(resSave2, null, 2));
    const memoryIdV2 = resSave2.memory_id;

    if (memoryIdV1 === memoryIdV2) {
      throw new Error("Lineage failed: Memory V2 should have a distinct memory_id from V1!");
    }

    // 3. Retrieve by context_id
    console.log("Retrieving snapshots log for context_id...");
    const resRet = await intelligenceGateway.retrieveMemory(null, "ctx_node_e2e_99");
    console.log("Retrieve results:", JSON.stringify(resRet, null, 2));
    if (resRet.memories.length !== 2) {
      throw new Error(`Expected exactly 2 versions in context log, got ${resRet.memories.length}`);
    }

    // Verify lineage chaining parent_memory_id
    const v1Record = resRet.memories[0];
    const v2Record = resRet.memories[1];
    if (v2Record.metadata.parent_memory_id !== v1Record.metadata.memory_id) {
      throw new Error("Lineage chaining failed: V2 parent_memory_id does not link back to V1 memory_id!");
    }

    // Verify fields merge values
    const mergedDomains = v2Record.snapshot.facts.technical_domains;
    if (!mergedDomains.includes("Node.js") || !mergedDomains.includes("AWS")) {
      throw new Error("Merge policy failed to combine technical domains!");
    }

    // 4. Search memory by text keyword
    console.log("Searching memories for 'react'...");
    const resSearch = await intelligenceGateway.searchMemory("react", "session_node_e2e_99");
    console.log("Search results:", JSON.stringify(resSearch, null, 2));
    if (resSearch.results.length === 0) {
      throw new Error("Search failed: did not match 'react' text query!");
    }

    console.log("\nSUCCESS: Memory Service compiled, structured, versioned and validated successfully E2E!");
  } catch (error) {
    console.error("E2E Verification Error:", error);
    process.exit(1);
  } finally {
    console.log("[MCP Client] Closing connection...");
    await intelligenceGateway.close();
    console.log("[MCP Client] Stdio transport connection closed.");
    console.log("Memory Service verification finished.");
  }
}

run();
