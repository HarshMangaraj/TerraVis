import { Queue } from "bullmq";
import IORedis from "ioredis";

export const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

connection.on("connect", () => console.log("Redis: connected"));
connection.on("ready", () => console.log("Redis: ready"));
connection.on("error", (err) => console.log("Redis ERROR:", err.message));

export const testQueue = new Queue("test-queue", { connection });