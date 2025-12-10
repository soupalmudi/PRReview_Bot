Architecture
============

Goals
-----
- Automate code review for PRs using LLMs.
- Produce structured, actionable findings (severity, category, message, file/line).
- Keep providers swappable (OpenAI, Cohere, HF).
- Run locally via Docker Compose; deploy to cloud later.

High-Level Design
-----------------
- Frontend (React + Vite)
  - Simple UI to submit PR metadata or paste a diff.
  - Displays findings with severity filters and source file grouping.
- Backend (Python + Flask)
  - REST endpoints: `POST /api/review`, `GET /api/health`.
  - Orchestrator splits diffs per file, builds prompts, calls the LLM client, and normalizes results.
  - Provider adapter (`llmClient`) hides vendor-specific details.
  - Basic PII/secret scrubber runs before calling LLMs.
- Queue/Future Scaling
  - For larger PRs, enqueue jobs (BullMQ/SQS) and stream partial results via SSE/WebSocket.

Data Model (draft)
------------------
- ReviewRequest: repo, prNumber, diff, filesChanged[], config (model, temperature, maxTokens, categories enabled).
- Finding: id, severity (`critical|major|minor|nit`), category (`bug|security|style|doc|perf`), filePath, line, message, suggestion.

LLM Flow (draft)
----------------
1) Receive request, validate payload size.
2) Scrub secrets (basic regex for keys, tokens).
3) Chunk diff by file; truncate long files with a summary note.
4) Prompt template instructs the model to return JSON array of findings.
5) Parse model output; fall back to safe defaults on parsing errors.
6) Return findings with diagnostics (tokens used, latency).

CI/CD (planned)
---------------
- GitHub Actions:
  - `lint` job: backend and frontend lint/tests.
  - `build` job: Docker image build and push.
  - `deploy` job (later): push to cloud.

Security Considerations (initial)
---------------------------------
- Never log raw diffs that may contain secrets.
- Rate limit public endpoints; require auth tokens for production.
- Keep provider keys in secrets managers.
- Add allowlist for outbound domains.

Open Questions
--------------
- Which provider(s) to prioritize for first milestone?
- Do we need GitHub App integration versus PAT-based polling?
- Preferred deployment target (AWS ECS/Fargate, GCP Cloud Run, others)?
