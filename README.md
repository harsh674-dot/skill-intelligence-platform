# Skill Intelligence Platform

AI-enabled competency and learning platform for capacity building in India's Official Statistical System (SIH26101).

## Problem

India's Official Statistical System requires continuous upskilling across diverse competencies, roles, and regions. Traditional training programs are static and do not adapt to individual skill gaps. This platform identifies competency gaps, recommends personalized learning resources, generates assessments from learning materials using AI, and provides analytics for administrators and employees.

## Key Features

- **Competency Engine** — Define and manage competencies, roles, and proficiency frameworks.
- **AI-Powered Assessments** — Generate questions from uploaded documents/learning materials using LLMs.
- **Personalized Learning** — Recommend courses and content based on competency gaps and role requirements.
- **Search & Vector RAG** — Semantic search over learning content and document embeddings.
- **Dashboard & Analytics** — Workforce analytics, progress tracking, and gap heatmaps.
- **Role-Based Access** — JWT-secured auth for Admin, Manager, and Employee personas.
- **3D Interactive UI** — Three.js-powered galaxy visualization for skill exploration.
- **Offline Demo Fallback** — Vercel-ready frontend with demo mode for showcases.

## Tech Stack

### Frontend
- Next.js 16 (App Router)
- React 19
- Tailwind CSS v4
- Three.js / React Three Fiber
- Lucide React
- canvas-confetti

### Backend
- FastAPI
- SQLAlchemy 2.0 + Alembic
- PostgreSQL + pgvector
- PyJWT + Argon2
- Sentence-Transformers / Transformers / Torch
- pypdf + python-docx

### Infrastructure
- Vercel (frontend deployment)
- PostgreSQL (Neon / local)
- Alembic migrations

## Project Structure

```
skill-intelligence-platform/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ThreeSkillGalaxy.tsx
│   │   ├── AdminStudio.tsx
│   │   ├── EmployeeDashboard.tsx
│   │   ├── WorkforceAnalytics.tsx
│   │   ├── AssessmentModal.tsx
│   │   ├── JudgeTourGuide.tsx
│   │   └── Navbar.tsx
│   ├── context/
│   │   └── LanguageContext.tsx
│   ├── lib/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── competency.py
│   │   │   │   ├── roles.py
│   │   │   │   ├── courses.py
│   │   │   │   ├── questions.py
│   │   │   │   ├── assessment.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── recommendations.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── learning.py
│   │   │   │   ├── search.py
│   │   │   │   └── ai_questions.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── adapters/
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   ├── seed.py
│   └── seed_demo.py
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/harsh674-dot/skill-intelligence-platform.git
cd skill-intelligence-platform
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` or at the repo root:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/skill_intelligence_db
JWT_SECRET_KEY=your_jwt_secret_key_here
ENVIRONMENT=development
```

Run database migrations:

```bash
alembic upgrade head
```

Seed demo data (optional):

```bash
python seed_demo.py
```

Start the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Neon pooler URL |
| `JWT_SECRET_KEY` | Secret for JWT encoding | Dev placeholder |
| `ENVIRONMENT` | App environment | `development` |

## API Overview

| Prefix | Purpose |
|--------|---------|
| `/api/health` | Health checks |
| `/api/auth` | Login, register, token refresh |
| `/api/competency` | Competency CRUD |
| `/api/roles` | Role management |
| `/api/courses` | Course catalog |
| `/api/questions` | Question bank |
| `/api/assessment` | Assessment lifecycle |
| `/api/recommendations` | AI recommendations |
| `/api/dashboard` | Analytics endpoints |
| `/api/learning` | Learning path & progress |
| `/api/search` | Semantic content search |
| `/api/ai-questions` | AI-generated questions |

## Database

- **SQLAlchemy 2.0** ORM with declarative models.
- **Alembic** for schema migrations.
- **pgvector** for embedding storage and similarity search.
- Key models: `User`, `Role`, `Competency`, `Course`, `Question`, `Assessment`, `AIQuestion`, `ContentChunk`.

## AI & RAG Pipeline

1. **Document Ingestion** — Upload PDF/DOCX via `/api/courses` or dedicated ingestion routes.
2. **Chunking** — Split content into semantic chunks.
3. **Embeddings** — Generate vector embeddings using Sentence-Transformers.
4. **Storage** — Persist chunks and embeddings in PostgreSQL with pgvector.
5. **Retrieval** — Vector search for quiz generation and content recommendations.
6. **Generation** — LLM-backed question generation from retrieved context.

## Deployment

### Frontend (Vercel)

The frontend is configured for Vercel with Next.js framework detection.

```bash
cd frontend
vercel deploy --prod
```

Set environment variables in the Vercel dashboard.

### Backend

Deploy the FastAPI app to any ASGI host (Render, Fly.io, AWS ECS, etc.):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Ensure `DATABASE_URL` and `JWT_SECRET_KEY` are set in production.

## Testing

```bash
cd backend
pytest tests/
```

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes with clear messages.
4. Push to the branch.
5. Open a Pull Request.

## License

This project is developed for the Smart India Hackathon (SIH26101).
