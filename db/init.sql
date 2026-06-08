CREATE TABLE candidates (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE,
  source TEXT DEFAULT 'webhook',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE logs (
  id SERIAL PRIMARY KEY,
  trace_id TEXT,
  level TEXT,
  event TEXT,
  payload JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE failed_jobs (
  id SERIAL PRIMARY KEY,
  job_id TEXT,
  queue_name TEXT,
  payload JSONB,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);