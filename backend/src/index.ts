import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { reviewRouter } from "./routes/review.js";

dotenv.config();

const app = express();
const port = process.env.PORT ? Number(process.env.PORT) : 5001;

app.use(cors());
app.use(express.json({ limit: "1mb" }));

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", uptime: process.uptime() });
});

app.use("/api/review", reviewRouter);

app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(err);
  res.status(500).json({ error: "Unexpected server error" });
});

app.listen(port, () => {
  console.log(`PR Review backend listening on ${port}`);
});
