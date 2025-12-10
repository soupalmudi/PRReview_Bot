import { OpenAI } from "openai";
import { Finding } from "../types.js";

const providerName = "openai";

interface LLMConfig {
  model: string;
  temperature?: number;
  maxTokens?: number;
}

interface LLMResult {
  provider: string;
  model: string;
  findings: Finding[];
  tokens?: number;
  truncated?: boolean;
}

export async function runLLMReview(prompt: string, config: LLMConfig): Promise<LLMResult> {
  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    return {
      provider: "mock",
      model: "offline",
      truncated: false,
      findings: [
        {
          id: "mock-1",
          severity: "minor",
          category: "style",
          message: "LLM key missing; returning mock feedback. Provide OPENAI_API_KEY to enable real analysis."
        }
      ]
    };
  }

  const client = new OpenAI({ apiKey });

  const completion = await client.responses.create({
    model: config.model,
    input: prompt,
    temperature: config.temperature ?? 0.2,
    max_output_tokens: config.maxTokens ?? 512
  });

  const content = completion.output[0]?.content[0];
  const text = content?.type === "output_text" ? content.text : "";

  const parsed = safeParseFindings(text);

  return {
    provider: providerName,
    model: config.model,
    findings: parsed,
    tokens: completion.usage?.output_tokens,
    truncated: completion.usage?.output_tokens
      ? completion.usage.output_tokens >= (config.maxTokens ?? 512)
      : false
  };
}

function safeParseFindings(raw: string): Finding[] {
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed as Finding[];
    }
  } catch (err) {
    console.warn("Failed to parse LLM output, returning fallback", err);
  }

  return [
    {
      id: "parse-fallback",
      severity: "nit",
      category: "doc",
      message: "Model output could not be parsed. Verify prompt and model settings."
    }
  ];
}
