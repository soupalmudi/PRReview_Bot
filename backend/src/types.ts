export type Severity = "critical" | "major" | "minor" | "nit";
export type Category = "bug" | "security" | "style" | "doc" | "perf";

export interface ReviewRequest {
  repo?: string;
  prNumber?: string;
  diff: string;
  filesChanged?: string[];
  config?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
  };
}

export interface Finding {
  id: string;
  severity: Severity;
  category: Category;
  filePath?: string;
  line?: number;
  message: string;
  suggestion?: string;
}

export interface ReviewResponse {
  findings: Finding[];
  diagnostics: {
    provider: string;
    model: string;
    latencyMs: number;
    tokens?: number;
    truncated?: boolean;
  };
}
