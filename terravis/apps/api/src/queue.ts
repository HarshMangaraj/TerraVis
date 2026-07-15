import { Queue } from "bullmq";
import IORedis from "ioredis";

// maxRetriesPerRequest: null is required by BullMQ specifically —
// it disables ioredis's default retry limit so BullMQ can manage retries itself
export const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

export const testQueue = new Queue("test-queue", { connection });