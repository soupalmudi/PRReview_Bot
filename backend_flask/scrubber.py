import re

SECRET_PATTERNS = [
  re.compile(r"(api|secret|token|key)[=:]\s*[\"']?([A-Za-z0-9_\\-]{16,})", re.IGNORECASE),
  re.compile(r"ghp_[A-Za-z0-9]{30,}"),
  re.compile(r"sk-[A-Za-z0-9]{20,}")
]


def scrub_secrets(text: str) -> str:
  scrubbed = text
  for pattern in SECRET_PATTERNS:
    scrubbed = pattern.sub("[REDACTED_SECRET]", scrubbed)
  return scrubbed
