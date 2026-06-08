const connection = {
  host: process.env.REDIS_HOST || "redis",
  port: 6379,
};

export default connection;