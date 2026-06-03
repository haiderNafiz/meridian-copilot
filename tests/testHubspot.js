
import { upsertContact } from "../src/services/hubspot.js";

// Test 1 — create a brand new candidate
const newCandidate = {
  email: "mei.hashimoto@outlook.com",
  first_name: "Mei",
  last_name: "Hashimoto",
  phone: "+1-415-782-0034",
  current_title: "Frontend Engineer",
};

// Test 2 — same candidate again (should UPDATE not duplicate)
const duplicateCandidate = {
  email: "tariq.oyelaran@gmail.com",  // already exists from your curl test
  first_name: "Tariq",
  last_name: "Oyelaran",
  phone: "+1-512-334-8821",
  current_title: "Senior Backend Engineer",
};

async function runTests() {
  console.log("--- Test 1: Create new contact ---");
  const result1 = await upsertContact(newCandidate);
  console.log("Result:", result1);

  console.log("\n--- Test 2: Upsert existing contact (should update) ---");
  const result2 = await upsertContact(duplicateCandidate);
  console.log("Result:", result2);
}

runTests().catch(console.error);
