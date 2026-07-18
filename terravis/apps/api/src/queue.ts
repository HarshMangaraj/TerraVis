import { Queue } from "bullmq";
import IORedis from "ioredis";

export const connection = new IORedis({
  host: "giving-mongrel-162100.upstash.io",
  port: 6379,
  password: process.env.REDIS_PASSWORD!,
  tls: {},
  maxRetriesPerRequest: null,
});

connection.on("ready", () => console.log("Redis: ready"));
connection.on("error", (err) => console.log("Redis ERROR:", err.message));

export const testQueue = new Queue("test-queue", { connection });