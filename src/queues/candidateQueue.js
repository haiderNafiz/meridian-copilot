import connection from "./redisConnection.js";
import { Queue } from "bullmq";

export const candidateQueue = new Queue("candidateQueue", {
  connection
});