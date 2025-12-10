Automated Pull Request Reviewer Bot
===================================

This project bootstraps an automated PR reviewer that uses LLMs to analyze code changes, surface risks, and draft actionable review comments. It ships with a Flask backend API and a React frontend. LLM integration is abstracted so you can swap providers (OpenAI, Cohere, HuggingFace) via configuration.

Quick Start
-----------
- Prereqs: Python 3.10+, pip, Node 18+ (for frontend), Docker (optional).
- Backend (Flask):
  1. `cd backend_flask && cp .env.example .env` and fill `OPENAI_API_KEY`.
  2. `python -m venv .venv && source .venv/bin/activate`
  3. `pip install -r requirements.txt`
  4. `flask run --app app --host 0.0.0.0 --port 5001`
- Frontend:
  1. `cd frontend`
  2. `npm install`
  3. `npm run dev`
- Docker Compose (builds Flask + frontend): `docker-compose up --build`

For a step-by-step guide (including troubleshooting), see `docs/running-locally.md`.

Project Layout
--------------
- `backend_flask/` – Flask API that accepts PR data, runs LLM-based analysis, and returns review items.
- `frontend/` – React UI for uploading diffs, configuring model providers, and viewing generated feedback.
- `docs/` – Architecture and roadmap notes.
- `docker-compose.yml` – Local orchestration for frontend + backend.

How it Works (current draft)
----------------------------
- The backend exposes:
  - `POST /api/review`: takes a PR payload `{ diff, filesChanged, repo, prNumber }`, runs analyzers, and returns structured findings grouped by severity.
  - `GET /api/health`: basic liveness probe.
- `backend_flask/llm_client.py` wraps provider calls; swap OpenAI or other clients by changing environment variables.
- `backend_flask/review_orchestrator.py` breaks the diff into file-level chunks, crafts prompts, and merges LLM responses into normalized findings.
- Frontend calls `POST /api/review` and renders findings with filtering by severity/category and allows prompt tweaks.

Security & Secrets
------------------
- Never commit API keys. Use `.env` files locally and secrets in CI/CD.
- Requests to LLMs redact obvious secrets from diffs (basic regex scrubber in the analyzer).

Roadmap (aligned to your milestones)
------------------------------------
1) Project Initialization – ✅ repo scaffold, architecture doc, Docker compose stubs.
2) Data Collection – add ingest jobs for historical PRs and labels (placeholder).
3) LLM Integration – implement provider drivers and prompt templates; add eval harness.
4) Backend Development – expand analyzers (security, performance, style); webhook ingestion for GitHub/GitLab.
5) Frontend – richer diff viewer, inline comments, provider settings.
6) Integration/Testing – contract tests for API, prompt unit tests, latency budgets.
7) Deployment – hardened Docker images, AWS ECS/Fargate or GCP Cloud Run.
8) Final Review/Docs – user guide, runbooks, threat model.

Next Steps
----------
- Fill in `.env` with your provider keys and org IDs.
- Implement real provider call in `backend_flask/llm_client.py` (or swap provider).
- Extend `frontend/src/components/ReviewResult.tsx` to support inline diff rendering.
- Wire GitHub webhooks to push PR events into the API.
