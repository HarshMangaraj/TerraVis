const form = new FormData();
const file = Bun.file("D:/ISRO-Hackathon/test.txt");
form.append("file", file, "test.txt");

const res = await fetch("http://localhost:3001/upload-test", {
  method: "POST",
  body: form,
});

const text = await res.text();
console.log("status:", res.status);
console.log("body:", text);