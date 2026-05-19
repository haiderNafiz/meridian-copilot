import express from 'express';
import { candidateQueue } from "./queues/candidateQueue.js";
import cors from 'cors';
import 'dotenv/config';

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS middleware
app.use(cors());
app.use(express.json());

// Add a test route
app.get('/', (req, res) => {
  res.send("Meridian Copilot Running");
});

app.post("/webhooks/form-submission", async (req, res) => {
  console.log("Webhook received:");

  await candidateQueue.add("new-candidate", {
    payload: req.body,
    receivedAt: new Date().toISOString()
  });

  console.log("Job added to queue");

  //console.log(req.body);

  res.json({
    success: true,
    message: "Candidate queued successfully"
  });
});

// Start the server and print the confirmation message
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
