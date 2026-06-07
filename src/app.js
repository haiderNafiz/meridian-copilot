import express from 'express';
import { candidateQueue } from "./queues/candidateQueue.js";
import healthRoutes from "./routes/healthRoutes.js";

import cors from 'cors';
import 'dotenv/config';
import pool from "./db/index.js";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json()); // <-- Crucial: This parses the incoming webhook data

app.get('/', (req, res) => {
  res.send('Meridian Copilot Running');
});

// --- Your Webhook Route Added Here ---
app.post("/webhooks/form-submission", async (req, res) => {
  console.log("Webhook received:");

  await candidateQueue.add(
    "new-candidate",
    {
      payload: req.body,
      receivedAt: new Date().toISOString()
    },
    {
      attempts: 3,

      backoff: {
        type: "exponential",
        delay: 2000
      }
    }
  );

  //console.log(req.body); // <-- This prints the data to your VS Code terminal

  console.log("Job added to queue");

  res.json({
    success: true,
    message: "Candidate queued successfully"
  });
});


app.use(
  "/",
  healthRoutes
);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});



// log api endpoint
app.get("/logs/:traceId", async (req, res) => {
  const { traceId } = req.params;

  const result = await pool.query(
    `
    SELECT *
    FROM logs
    WHERE trace_id = $1
    ORDER BY created_at ASC
    `,
    [traceId]
  );

  res.json(result.rows);
});
