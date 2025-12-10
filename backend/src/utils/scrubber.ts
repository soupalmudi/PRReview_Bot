const secretPatterns = [
  /(api|secret|token|key)[=:]\s*["']?([A-Za-z0-9_\-]{16,})/gi,
  /ghp_[A-Za-z0-9]{30,}/g,
  /sk-[A-Za-z0-9]{20,}/g
];

export function scrubSecrets(input: string): string {
  let output = input;

  for (const pattern of secretPatterns) {
    output = output.replace(pattern, "[REDACTED_SECRET]");
  }

  return output;
}
