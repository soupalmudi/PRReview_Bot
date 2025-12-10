import { Router } from "express";
import { z } from "zod";
import { orchestrateReview } from "../services/reviewOrchestrator.js";

const requestSchema = z.object({
  repo: z.string().optional(),
  prNumber: z.string().optional(),
  diff: z.string().min(1, "diff is required"),
  filesChanged: z.array(z.string()).optional(),
  config: z
    .object({
      model: z.string().optional(),
      temperature: z.number().min(0).max(2).optional(),
      maxTokens: z.number().int().optional()
    })
    .optional()
});

export const reviewRouter = Router();

reviewRouter.post("/", async (req, res) => {
  const parsed = requestSchema.safeParse(req.body);

  if (!parsed.success) {
    return res.status(400).json({ error: parsed.error.flatten() });
  }

  try {
    const result = await orchestrateReview(parsed.data);
    res.json(result);
  } catch (err) {
    console.error("review error", err);
    res.status(500).json({ error: "Failed to generate review" });
  }
});
