import { Worker } from "bullmq";

const worker = new Worker(
  "candidateQueue",
  async (job) => {

    console.log("Worker processing job...");

    console.log("Job name:", job.name);

    console.log("Candidate payload:");
    console.log(job.data);

  },
  {
    connection: {
      host: "127.0.0.1",
      port: 6379
    }
  }
);

worker.on("completed", (job) => {
  console.log(`Job ${job.id} completed`);
});

worker.on("failed", (job, err) => {
  console.log(`Job failed: ${err.message}`);
});