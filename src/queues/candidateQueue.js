import { Queue } from "bullmq";

export const candidateQueue = new Queue("candidateQueue", {
  connection: {
    host: "127.0.0.1",
    port: 6379
  }
});