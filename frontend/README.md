# Skill Intelligence Platform Frontend

Next.js 16 App Router frontend for the Skill Intelligence Platform. The UI calls the FastAPI backend directly; it does not include an offline or mock API fallback.

## Requirements

- Node.js 20 or newer
- A running PostgreSQL-backed FastAPI backend

## Run the backend

From the repository root:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `backend/.env` or a root `.env` with at least:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/skill_intelligence
JWT_SECRET_KEY=replace-with-a-long-random-secret
```

Add the frontend origin to `ALLOWED_ORIGINS` when the frontend and API use different origins. Then initialize and start the API:

```bash
alembic upgrade head
python seed_demo.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The health endpoint is `http://localhost:8000/health`; application routes use `/api`. Seeded demo accounts use the password `Demo@12345`.

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

`NEXT_PUBLIC_API_URL` controls where the browser sends API requests:

- Unset or `/api`: use same-origin `/api` and `/health` requests. Local `next dev` rewrites these paths to `http://localhost:8000`.
- `http://localhost:8000`: call a direct local backend. The backend must allow the frontend origin through CORS.
- `https://api.example.com`: call a remote backend origin. Do not include a trailing slash.

For a same-origin production deployment, leave `NEXT_PUBLIC_API_URL` unset and configure the hosting platform to proxy `/api` and `/health` to the FastAPI service. For a separate backend host, set `NEXT_PUBLIC_API_URL` to the backend origin and include the frontend origin in the backend `ALLOWED_ORIGINS` setting. `NEXT_PUBLIC_API_URL` is public configuration, not a secret.

## Build and checks

```bash
npm run lint
npm run build
```

For Vercel or another production platform, set `NEXT_PUBLIC_API_URL` in the platform environment when the API is not served from the frontend origin. Rebuild/redeploy after changing it because Next.js inlines public environment values in the client bundle.
