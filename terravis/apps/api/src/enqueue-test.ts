console.log("script started");

try {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  const res = await fetch("http://127.0.0.1:3001/enqueue-test", {
    method: "POST",
    signal: controller.signal,
  });
  clearTimeout(timeout);

  const text = await res.text();
  console.log("status:", res.status);
  console.log("body:", text);
} catch (err) {
  console.log("FETCH ERROR:", err);
}

console.log("script ended");