import json
import os
from typing import Any, Dict, List

from openai import OpenAI


def run_llm_review(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
  api_key = os.getenv("OPENAI_API_KEY")

  if not api_key:
    return {
      "provider": "mock",
      "model": "offline",
      "truncated": False,
      "findings": [{
        "id": "mock-1",
        "severity": "minor",
        "category": "style",
        "message": "LLM key missing; returning mock feedback. Set OPENAI_API_KEY to enable real analysis."
      }]
    }

  client = OpenAI(api_key=api_key)

  completion = client.chat.completions.create(
    model=config.get("model"),
    messages=[
      {
        "role": "system",
        "content": (
          "You are an expert software reviewer. "
          "Given a git diff, identify issues and suggestions. "
          "Respond strictly as JSON: an object with a single field `findings`, "
          "where `findings` is an array of objects with fields: severity, category, "
          "message, filePath, line, suggestion. Do not include prose or code fences."
        )
      },
      {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"},
    temperature=config.get("temperature", 0.2),
    max_tokens=config.get("maxTokens", 512)
  )

  message = completion.choices[0].message if completion.choices else None
  text = message.content if message else ""
  findings = safe_parse_findings(text or "")

  finish_reason = completion.choices[0].finish_reason if completion.choices else None

  return {
    "provider": "openai",
    "model": config.get("model"),
    "findings": findings,
    "tokens": completion.usage.completion_tokens if completion.usage else None,
    "truncated": finish_reason == "length"
  }


def safe_parse_findings(raw: str) -> List[Dict[str, Any]]:
  try:
    parsed = json.loads(raw)
    if isinstance(parsed, list):
      return parsed
    if isinstance(parsed, dict) and isinstance(parsed.get("findings"), list):
      return parsed["findings"]
  except Exception:
    pass

  return [{
    "id": "parse-fallback",
    "severity": "nit",
    "category": "doc",
    "message": "Model output could not be parsed. Verify prompt and model settings."
  }]
