import { randomUUID } from "crypto";
import { ReviewRequest, ReviewResponse, Finding } from "../types.js";
import { runLLMReview } from "./llmClient.js";
import { scrubSecrets } from "../utils/scrubber.js";

const defaultConfig = {
  model: process.env.OPENAI_MODEL || "gpt-4o-mini",
  temperature: 0.2,
  maxTokens: 512
};

export async function orchestrateReview(request: ReviewRequest): Promise<ReviewResponse> {
  const started = performance.now();

  const scrubbedDiff = scrubSecrets(request.diff);
  const config = { ...defaultConfig, ...(request.config || {}) };

  const prompt = buildPrompt({
    diff: scrubbedDiff,
    repo: request.repo,
    prNumber: request.prNumber,
    filesChanged: request.filesChanged
  });

  const llmResult = await runLLMReview(prompt, config);
  const findings = normalizeFindings(llmResult.findings);

  const latencyMs = Math.round(performance.now() - started);

  return {
    findings,
    diagnostics: {
      provider: llmResult.provider,
      model: llmResult.model,
      latencyMs,
      tokens: llmResult.tokens,
      truncated: llmResult.truncated
    }
  };
}

function buildPrompt(input: { diff: string; repo?: string; prNumber?: string; filesChanged?: string[] }) {
  const header = [
    "You are an expert software reviewer.",
    "Given a git diff, identify issues and suggestions.",
    "Respond strictly as JSON array of findings with fields: severity, category, message, filePath, line, suggestion."
  ].join(" ");

  const meta = [
    input.repo ? `Repository: ${input.repo}` : null,
    input.prNumber ? `PR: ${input.prNumber}` : null,
    input.filesChanged?.length ? `Files changed: ${input.filesChanged.join(", ")}` : null
  ]
    .filter(Boolean)
    .join(" | ");

  return `${header}\n${meta}\nDiff:\n${input.diff}`;
}

function normalizeFindings(raw: Finding[]): Finding[] {
  return raw.map((item) => ({
    id: item.id || randomUUID(),
    severity: item.severity || "minor",
    category: item.category || "style",
    filePath: item.filePath,
    line: item.line,
    message: item.message || "Unspecified issue",
    suggestion: item.suggestion
  }));
}
