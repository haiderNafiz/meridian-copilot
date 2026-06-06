import { Worker } from "bullmq";
import connection from "../redisConnection.js";
import pool from "../../db/index.js";
import { createStageTimer } from "../../utils/timer.js";

import {
  sendNewCandidateAlert
} from "../../services/slackService.js";

import {
  upsertContact
} from "../../services/hubspot.js";

import {
  saveFailedJob
}
from "../../services/deadLetterService.js";

import { logger } from "../../utils/logger.js";

//const jobTimer = startTimer();


const worker = new Worker(
  "candidateQueue",
  async job => {

    //console.log(
      //`Processing Job ${job.id}`
    //);

    //console.log(
      //`Attempt ${job.attemptsMade + 1}`
    //);

    
    const timer = createStageTimer();
    const traceId = job.id;
    const payload = job.data.payload;
    const email = payload.email;

    logger.info("job.attempt", {
      jobId: job.id,
      attempt: job.attemptsMade + 1
    });


    //console.log(
      //"Processing:",
      //job.data
    //);

    logger.info("job.processing.started", {
      traceId,
      jobId: job.id,
      attempt: job.attemptsMade + 1,
      queue: "candidateQueue"
    });

    //const jobId = job.id;
    //const payload = job.data.payload;
    //const email = payload.email;

    
    // Retry testing
    if (email === "fail@test.com") {
      throw new Error(
        "Intentional test failure"
      );
    }

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

    //console.log(
      //"Saved to database"
    //);

    const dbTiming = timer.mark("db");

    logger.info("db.insert.success", {
      traceId,
      email,
      jobId: job.id,
      stage:dbTiming.stage,
      durationMs: dbTiming.durationMs
  
    });

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

    //console.log(
      //"Calling HubSpot..."
    //);

    logger.info("hubspot.sync.started", {traceId, email });

    try {

      const hubspotResult =
        await upsertContact(hubspotCandidate);

      //console.log(
        //"HubSpot completed"
      //);

      logger.info("hubspot.sync.success", {
        traceId,
        email,
        hubspotId: hubspotResult.hubspot_id,
        action: hubspotResult.action,
        ...timer.mark("hubspot"),
      });

      console.log(
        "HubSpot:",
        hubspotResult
      );

    } catch (error) {

      //console.error(
        //"HubSpot sync failed:",
        //error.message
      //);

      logger.error("hubspot.sync.failed", {
        traceId,
        email,
        error: error.message
      });

    }

    //console.log(
      //"Calling Slack..."
    //);

    logger.info("slack.notification.started", {
      traceId,
      email
      
    });

    try {

      await sendNewCandidateAlert(email,source);

    //console.log(
      //"Slack alert sent"
    //);

      logger.info("slack.notification.sent", {
        traceId,
        email,
        ...timer.mark("slack"),
      });

    } catch (error) {
      logger.error("slack.notification.failed", {
        traceId,
        email,
        error: error.message,
      });

    }

  },
  { connection }
);



// Job completed event
worker.on(
  "completed",
  job => {

    console.log(
      `Job ${job.id} completed successfully`
    );

  }
);


// Job failed
//worker.on(
  //"failed",
  //(job, err) => {

    //console.error(
      //`Job ${job.id} failed on attempt ${job.attemptsMade}`
    //);

    //console.error(
      //err.message
    //);

  //}
//);

//worker.on(
  //"failed",
  //async (job, err) => {

    //console.error(
      //`Job ${job.id} failed`
    //);

    //await saveFailedJob(
      //job,
      //err
    //);

    //console.log(
      //"Saved to DLQ table"
    //);

  //}
//);

//failed even + DLQ

worker.on(
  "failed",
  async (job, err) => {

    console.error(
      `Job ${job.id} failed on attempt ${job.attemptsMade}`
    );

    if(
      job.attemptsMade ===
      job.opts.attempts
    ){

      await saveFailedJob(
        job,
        err
      );

      console.log(
        "Final failure saved to DLQ"
      );

    }

  }
);


export default worker;