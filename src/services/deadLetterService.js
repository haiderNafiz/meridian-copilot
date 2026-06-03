import pool from "../db/index.js";

export async function saveFailedJob(
  job,
  error
) {

  await pool.query(
    `
    INSERT INTO failed_jobs
    (
      job_id,
      queue_name,
      payload,
      error_message
    )
    VALUES
    (
      $1,
      $2,
      $3,
      $4
    )
    `,
    [
      String(job.id),
      "candidateQueue",
      JSON.stringify(job.data),
      error.message
    ]
  );

}