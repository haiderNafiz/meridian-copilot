import pool from "./index.js";

async function initDB() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS candidates (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        source TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);

    console.log("Candidates table created");
  } catch (err) {
    console.error(err);
  }
}

initDB();