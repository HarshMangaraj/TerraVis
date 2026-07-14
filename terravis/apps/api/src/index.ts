import express from "express";
import multer from "multer";
import { uploadFile } from "./storage";

const app = express();
const upload = multer(); // handles multipart/form-data file uploads in memory

app.post("/upload-test", upload.single("file"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "no file provided" });

  const url = await uploadFile(
    `test/${Date.now()}-${req.file.originalname}`,
    req.file.buffer,
    req.file.mimetype
  );

  res.json({ url });
});

app.listen(3001, () => console.log("api running on :3001"));