import IORedis from "ioredis";

console.log("connecting...");

const connection = new IORedis({
  host: "giving-mongrel-162100.upstash.io",
  port: 6379,
  password: "YOUR_PASSWORD_HERE", // paste it directly, no URL encoding needed here
  tls: {}, // enables TLS/SSL, required by Upstash
  maxRetriesPerRequest: null,
  retryStrategy: () => null,
});

connection.on("connect", () => console.log("connected (TCP established)"));
connection.on("ready", () => console.log("READY — auth succeeded"));
connection.on("error", (err) => console.log("ERROR:", err.message));

setTimeout(() => {
  console.log("done, exiting");
  process.exit(0);
}, 5000);