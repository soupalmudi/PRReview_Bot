Running Locally
===============

Prereqs
-------
- Python 3.10+ and pip
- Node 18+ (for the frontend)
- Docker (optional, for compose)

Backend (Flask)
---------------
1) `cd backend_flask`
2) `cp .env.example .env` and set `OPENAI_API_KEY=...` (keep this file out of git).
3) `python -m venv .venv && source .venv/bin/activate`
4) Install deps (includes the pinned httpx version expected by the OpenAI client):  
   `pip install --upgrade --force-reinstall -r requirements.txt`
5) Run the API:  
   `FLASK_APP=app flask run --host 0.0.0.0 --port 5001`
6) Health check: `curl http://127.0.0.1:5001/api/health`

Frontend (Vite/React)
---------------------
1) In a new shell: `cd frontend`
2) Install: `npm install`
3) Start dev server: `npm run dev` (opens http://localhost:5173)
4) API target: defaults to `http://localhost:5001`. To point elsewhere, create `frontend/.env` with:  
   `VITE_API_BASE=http://your-backend-host:5001`

Docker Compose (optional)
-------------------------
From repo root: `docker-compose up --build`  
Frontend will serve on 5173, backend on 5001 (see `docker-compose.yml` for overrides).

Troubleshooting
---------------
- OpenAI client errors about `proxies`: ensure `pip install --upgrade --force-reinstall -r requirements.txt` so httpx is pinned.
- Node failing to start due to missing ICU libs: reinstall Node via Homebrew (`brew reinstall node`) or use `nvm install 20 && nvm use 20`.
