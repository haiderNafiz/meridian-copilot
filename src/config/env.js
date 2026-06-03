import dotenv from "dotenv";

dotenv.config();

export default {
  PORT: process.env.PORT,
  DATABASE_URL: process.env.DATABASE_URL,
  REDIS_HOST: process.env.REDIS_HOST,
  REDIS_PORT: process.env.REDIS_PORT,
  SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN,
  SLACK_CHANNEL_ID: process.env.SLACK_CHANNEL_ID,
  HUBSPOT_ACCESS_TOKEN:
    process.env.HUBSPOT_ACCESS_TOKEN
};