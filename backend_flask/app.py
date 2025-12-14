import hashlib
import hmac
import os
import time
from typing import Dict, List

import httpx
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from review_orchestrator import orchestrate_review

ps_start = time.time()

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
  return jsonify({"status": "ok", "uptime": time.time() - ps_start})


@app.post("/api/review")
def review():
  payload = request.get_json(silent=True) or {}

  try:
    result = orchestrate_review(payload)
    return jsonify(result)
  except ValueError as e:
    return jsonify({"error": str(e)}), 400
  except Exception as e:
    app.logger.exception("review error")
    return jsonify({"error": "Failed to generate review"}), 500


@app.post("/webhook")
def github_webhook():
  secret = os.getenv("GITHUB_WEBHOOK_SECRET")
  app_id = os.getenv("GITHUB_APP_ID")
  private_key = (os.getenv("GITHUB_PRIVATE_KEY") or "").replace("\\n", "\n")
  api_url = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")

  if not (secret and app_id and private_key):
    return jsonify({"error": "GitHub App config missing"}), 500

  signature = request.headers.get("X-Hub-Signature-256")
  event = request.headers.get("X-GitHub-Event")
  body = request.data or b""

  if not verify_signature(secret, signature, body):
    return jsonify({"error": "Invalid signature"}), 401

  payload = request.get_json(silent=True) or {}
  action = payload.get("action")

  if event != "pull_request" or action not in {"opened", "reopened", "synchronize"}:
    return jsonify({"status": "ignored"})

  installation_id = payload.get("installation", {}).get("id")
  pr = payload.get("pull_request", {})
  repo = payload.get("repository", {})

  if not installation_id or not pr or not repo:
    return jsonify({"error": "Invalid payload"}), 400

  repo_full = repo.get("full_name", "")
  owner = repo.get("owner", {}).get("login")
  repo_name = repo.get("name")
  pr_number = pr.get("number")
  head_sha = pr.get("head", {}).get("sha")

  try:
    token = create_installation_token(app_id, private_key, installation_id, api_url)
    diff = fetch_pr_diff(api_url, owner, repo_name, pr_number, token)
    review_result = orchestrate_review({
      "diff": diff,
      "repo": repo_full,
      "prNumber": pr_number,
      "filesChanged": []  # optional; can be expanded later
    })
    if head_sha:
      post_inline_comments(api_url, owner, repo_name, pr_number, head_sha, token, review_result.get("findings") or [])
    comment_body = format_comment(review_result)
    post_pr_comment(api_url, owner, repo_name, pr_number, token, comment_body)
    return jsonify({"status": "ok"})
  except Exception as e:
    app.logger.exception("webhook error")
    return jsonify({"error": "Webhook processing failed"}), 500


def verify_signature(secret: str, signature: str, body: bytes) -> bool:
  if not signature or not signature.startswith("sha256="):
    return False
  digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
  expected = f"sha256={digest}"
  return hmac.compare_digest(expected, signature)


def create_installation_token(app_id: str, private_key: str, installation_id: int, api_url: str) -> str:
  now = int(time.time())
  payload = {"iat": now - 60, "exp": now + (8 * 60), "iss": app_id}
  app_jwt = jwt.encode(payload, private_key, algorithm="RS256")

  url = f"{api_url}/app/installations/{installation_id}/access_tokens"
  headers = {
    "Authorization": f"Bearer {app_jwt}",
    "Accept": "application/vnd.github+json"
  }
  with httpx.Client(timeout=10) as client:
    resp = client.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]


def fetch_pr_diff(api_url: str, owner: str, repo: str, pr_number: int, token: str) -> str:
  url = f"{api_url}/repos/{owner}/{repo}/pulls/{pr_number}"
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3.diff"
  }
  with httpx.Client(timeout=15) as client:
    resp = client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def post_pr_comment(api_url: str, owner: str, repo: str, pr_number: int, token: str, body: str) -> None:
  url = f"{api_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
  }
  payload = {"body": body}
  with httpx.Client(timeout=10) as client:
    resp = client.post(url, headers=headers, json=payload)
    resp.raise_for_status()


def post_inline_comments(
  api_url: str,
  owner: str,
  repo: str,
  pr_number: int,
  commit_sha: str,
  token: str,
  findings: List[Dict],
  max_comments: int = 8
) -> None:
  """
  Create inline PR review comments on specific files/lines when we have that info.
  GitHub requires the commit SHA and file path/line numbers that exist in the diff.
  """
  url = f"{api_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
  }

  comments_posted = 0

  with httpx.Client(timeout=10) as client:
    for f in findings:
      if comments_posted >= max_comments:
        break

      path = f.get("filePath")
      line = f.get("line")
      if not path or not isinstance(line, int):
        continue

      severity = (f.get("severity") or "").capitalize()
      category = f.get("category") or ""
      message = f.get("message") or "Issue detected"
      suggestion = f.get("suggestion")

      body_lines = [f"**{severity} [{category}]** {message}"]
      if suggestion:
        body_lines.append(f"Suggestion: {suggestion}")
      body = "\n\n".join(body_lines)

      payload = {
        "commit_id": commit_sha,
        "path": path,
        "side": "RIGHT",
        "line": line,
        "body": body
      }

      resp = client.post(url, headers=headers, json=payload)
      # If inline placement fails (e.g., line not in diff), skip and continue.
      if resp.status_code < 300:
        comments_posted += 1
      else:
        app.logger.info("inline comment skipped for %s:%s (%s): %s", path, line, resp.status_code, resp.text)


def format_comment(result: Dict) -> str:
  findings: List[Dict] = result.get("findings") or []
  diagnostics = result.get("diagnostics") or {}
  lines = ["### Automated Review Findings"]
  if not findings:
    lines.append("\nNo findings.")
  else:
    for f in findings:
      sev = f.get("severity", "").capitalize()
      cat = f.get("category", "")
      path = f.get("filePath") or "n/a"
      line = f.get("line") or "n/a"
      msg = f.get("message", "")
      sug = f.get("suggestion")
      bullet = f"- **{sev}** [{cat}] {path}:{line} — {msg}"
      if sug:
        bullet += f" Suggestion: {sug}"
      lines.append(bullet)
  model = diagnostics.get("model")
  latency = diagnostics.get("latencyMs")
  footer_parts = []
  if model:
    footer_parts.append(f"Model: {model}")
  if latency:
    footer_parts.append(f"Latency: {latency} ms")
  if footer_parts:
    lines.append("\n" + " | ".join(footer_parts))
  return "\n".join(lines)


if __name__ == "__main__":
  port = int(os.getenv("PORT", 5001))
  app.run(host="0.0.0.0", port=port, debug=True)
