import IORedis from "ioredis";

console.log("connecting...");

const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
  retryStrategy: () => null, // disable auto-retry so we see ONE clean attempt, not a storm
});

connection.on("connect", () => console.log("connected (TCP established)"));
connection.on("ready", () => console.log("READY — auth succeeded"));
connection.on("error", (err) => console.log("ERROR:", err.message));

setTimeout(() => {
  console.log("done, exiting");
  process.exit(0);
}, 5000);