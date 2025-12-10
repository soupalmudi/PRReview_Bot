import time
import uuid
from typing import Any, Dict, List

from llm_client import run_llm_review
from scrubber import scrub_secrets

DEFAULT_CONFIG = {
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "maxTokens": 512
}


def orchestrate_review(payload: Dict[str, Any]) -> Dict[str, Any]:
  started = time.time()

  diff = payload.get("diff")
  if not diff or not isinstance(diff, str):
    raise ValueError("diff is required")

  config = {**DEFAULT_CONFIG, **(payload.get("config") or {})}

  prompt = build_prompt({
    "diff": scrub_secrets(diff),
    "repo": payload.get("repo"),
    "prNumber": payload.get("prNumber"),
    "filesChanged": payload.get("filesChanged")
  })

  llm_result = run_llm_review(prompt, config)
  findings = normalize_findings(llm_result["findings"])

  return {
    "findings": findings,
    "diagnostics": {
      "provider": llm_result["provider"],
      "model": llm_result["model"],
      "latencyMs": int((time.time() - started) * 1000),
      "tokens": llm_result.get("tokens"),
      "truncated": llm_result.get("truncated", False)
    }
  }


def build_prompt(data: Dict[str, Any]) -> str:
  header = (
    "You are an expert software reviewer. "
    "Given a git diff, identify issues and suggestions. "
    "Respond strictly as JSON array of findings with fields: "
    "severity, category, message, filePath, line, suggestion."
  )

  meta = " | ".join(filter(None, [
    f"Repository: {data.get('repo')}" if data.get("repo") else None,
    f"PR: {data.get('prNumber')}" if data.get("prNumber") else None,
    f"Files changed: {', '.join(data.get('filesChanged') or [])}" if data.get("filesChanged") else None
  ]))

  return f"{header}\n{meta}\nDiff:\n{data['diff']}"


def normalize_findings(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  normalized = []
  for item in raw:
    normalized.append({
      "id": item.get("id") or str(uuid.uuid4()),
      "severity": item.get("severity", "minor"),
      "category": item.get("category", "style"),
      "filePath": item.get("filePath"),
      "line": item.get("line"),
      "message": item.get("message", "Unspecified issue"),
      "suggestion": item.get("suggestion")
    })
  return normalized
