function baseLog(level, event, data = {}) {
  console.log(
    JSON.stringify({
      level,
      event,
      timestamp: new Date().toISOString(),
      ...data
    })
  );
}

export const logger = {
  info: (event, data) => baseLog("info", event, data),
  warn: (event, data) => baseLog("warn", event, data),
  error: (event, data) => baseLog("error", event, data),
  debug: (event, data) => baseLog("debug", event, data),
};