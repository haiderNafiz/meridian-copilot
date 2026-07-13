import { Queue } from "bullmq";
import dotenv from "dotenv";
dotenv.config();

// Resolve local redis connection
const connection = {
  host: process.env.REDIS_HOST === "redis" ? "localhost" : (process.env.REDIS_HOST || "localhost"),
  port: 6379,
};

const candidateQueue = new Queue("candidateQueue", { connection });

async function triggerJobs() {
  console.log(`Triggering E2E jobs using Redis at ${connection.host}:${connection.port}`);

  // Job 1: Valid candidate application containing "CV" keyword
  console.log("Enqueueing Job 1: Valid application...");
  const job1 = await candidateQueue.add("new-candidate", {
    payload: {
      email: "mei.e2e@outlook.com",
      name: "Mei Hashimoto E2E",
      text: "Hello, attached is my CV for the Frontend Engineer position."
    }
  });
  console.log(`Job 1 enqueued with ID: ${job1.id}`);

  // Job 2: Withdrawal request containing "withdraw" keyword
  console.log("Enqueueing Job 2: Withdrawal request...");
  const job2 = await candidateQueue.add("new-candidate", {
    payload: {
      email: "withdraw.e2e@example.com",
      name: "E2E Withdraw",
      text: "Please withdraw my resume application."
    }
  });
  console.log(`Job 2 enqueued with ID: ${job2.id}`);

  console.log("Jobs successfully enqueued!");
  await candidateQueue.close();
}

triggerJobs().catch(console.error);
