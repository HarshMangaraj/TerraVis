const res = await fetch("http://localhost:3001/enqueue-test", { method: "POST" });
const text = await res.text();
console.log("status:", res.status);
console.log("body:", text);