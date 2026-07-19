import { Worker } from "bullmq";
import { connection } from "./queue";

const worker = new Worker(
  "test-queue",
  async (job) => {
    console.log("Picked up job:", job.id, job.data);

    // Call the Python FastAPI service with the job payload
    const res = await fetch("http://127.0.0.1:8000/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_id: job.id,
        task_type: "cloud_removal", // hardcoded for this test
        input_url: "https://example.com/test.tif",
      }),
    });

    const result = await res.json();
    console.log("FastAPI responded:", result);

    return result;
  },
  { connection }
);

worker.on("completed", (job) => {
  console.log(`Job ${job.id} completed`);
});

connection.on("ready", () => console.log("Redis: ready"));
connection.on("error", (err) => console.log("Redis ERROR:", err.message));

console.log("Worker listening on test-queue...");