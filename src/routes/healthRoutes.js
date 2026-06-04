import express from "express";
import pool from "../db/index.js";
import IORedis from "ioredis";

const router = express.Router();

const redis = new IORedis({
  host: "127.0.0.1",
  port: 6379
});

router.get(
  "/health",
  (req, res) => {

    res.json({
      status: "UP",
      timestamp: new Date()
    });

  }
);

router.get(
  "/health/database",
  async (req, res) => {

    try {

      await pool.query(
        "SELECT 1"
      );

      res.json({
        status: "UP",
        database: "connected"
      });

    }
    catch(error){

      res.status(500).json({
        status: "DOWN",
        database: "unreachable"
      });

    }

  }
);


router.get(
  "/health/redis",
  async (req, res) => {

    try {

      const result =
        await redis.ping();

      res.json({
        status: "UP",
        redis: result
      });

    }
    catch(error){

      res.status(500).json({
        status: "DOWN",
        redis: "unreachable"
      });

    }

  }
);

export default router;