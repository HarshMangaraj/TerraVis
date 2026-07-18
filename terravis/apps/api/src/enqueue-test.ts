const res = await fetch("http://127.0.0.1:3001/enqueue-test", { method: "POST" });
const text = await res.text();
console.log("status:", res.status);
console.log("body:", text);