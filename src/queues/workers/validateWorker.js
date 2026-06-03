import { Worker } from "bullmq";
import connection from "../redisConnection.js";
import pool from "../../db/index.js";

import {
  sendNewCandidateAlert
} from "../../services/slackService.js";

import {
  upsertContact
} from "../../services/hubspot.js";

const worker = new Worker(
  "candidateQueue",
  async job => {

    console.log(
      `Processing Job ${job.id}`
    );

    console.log(
      `Attempt ${job.attemptsMade + 1}`
    );

    console.log(
      "Processing:",
      job.data
    );

    const payload = job.data.payload;

    const email = payload.email;

    // Retry testing
    //if (email === "fail@test.com") {
      //throw new Error(
        //"Intentional test failure"
      //);
    //}

    const source = "form_submission";

    const result = await pool.query(
      `
      INSERT INTO candidates(email, source)
      VALUES ($1, $2)
      ON CONFLICT (email)
      DO NOTHING
      RETURNING *
      `,
      [email, source]
    );

    console.log(
      "Saved to database"
    );

    let candidate;

    if (result.rows.length > 0) {

      candidate = result.rows[0];

    } else {

      const existing =
        await pool.query(
          `
          SELECT *
          FROM candidates
          WHERE email = $1
          `,
          [email]
        );

      candidate = existing.rows[0];
    }

    const hubspotCandidate = {
      email: payload.email,
      first_name: payload.name || "",
      last_name: "",
      phone: "",
      current_title: ""
    };

    console.log(
      "Calling HubSpot..."
    );

    try {

      const hubspotResult =
        await upsertContact(
          hubspotCandidate
        );

      console.log(
        "HubSpot completed"
      );

      console.log(
        "HubSpot:",
        hubspotResult
      );

    } catch (error) {

      console.error(
        "HubSpot sync failed:",
        error.message
      );

    }

    console.log(
      "Calling Slack..."
    );

    await sendNewCandidateAlert(
      email,
      source
    );

    console.log(
      "Slack alert sent"
    );

  },
  { connection }
);


// Job completed
worker.on(
  "completed",
  job => {

    console.log(
      `Job ${job.id} completed successfully`
    );

  }
);


// Job failed
worker.on(
  "failed",
  (job, err) => {

    console.error(
      `Job ${job.id} failed on attempt ${job.attemptsMade}`
    );

    console.error(
      err.message
    );

  }
);

export default worker;