import pool from "../db/index.js";

function baseLog(level, event, data = {}) {
  const logObject = {
    level,
    event,
    timestamp: new Date().toISOString(),
    ...data,
  };

  console.log(JSON.stringify(logObject));

  // async DB write (fire and forget)
  pool.query(
    `
    INSERT INTO logs(trace_id, level, event, payload)
    VALUES ($1, $2, $3, $4)
    `,
    [
      data.traceId || null,
      level,
      event,
      JSON.stringify(data),
    ]
  ).catch(err => {
    console.error("Log DB insert failed:", err.message);
  });
}

export const logger = {
  info: (event, data) => baseLog("info", event, data),
  warn: (event, data) => baseLog("warn", event, data),
  error: (event, data) => baseLog("error", event, data),
  debug: (event, data) => baseLog("debug", event, data),
};