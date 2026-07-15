import { Worker } from "bullmq";
import { connection } from "./queue";

// This worker listens on "test-queue" and runs this function
// whenever a new job appears in it
const worker = new Worker(
  "test-queue",
  async (job) => {
    console.log("Picked up job:", job.id, job.data);
    return { done: true };
  },
  { connection }
);

worker.on("completed", (job) => {
  console.log(`Job ${job.id} completed`);
});

console.log("Worker listening on test-queue...");