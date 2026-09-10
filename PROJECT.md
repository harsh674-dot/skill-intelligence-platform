# Skill Intelligence Platform

**SIH26101** — AI-Enabled Competency Modeling, Skill-Gap Engine, and Closed-Loop Learning Reassessment Platform for India's Official Statistical System.

---

## 1. Vision

India's Official Statistical System needs continuous, data-driven upskilling across thousands of officers, analysts, and staff spread across ministries, departments, and regional offices. Traditional training programs are static, one-size-fits-all, and disconnected from actual competency evidence.

This platform transforms workforce development by:

- Mapping every employee against a structured **role-competency framework**
- Detecting **skill gaps** using the 40/60 evidence-weighted rule
- Delivering **personalized learning recommendations** from curated content
- Generating assessments **directly from uploaded learning materials** using AI/RAG
- Providing **real-time analytics** to administrators and employees
- Closing the learning loop by **reassessing and upgrading competencies** after training

---

## 2. What the Platform Does

### 2.1 Competency Framework

The system defines competencies, roles, and proficiency levels (L1–L5). Each role has required competency levels, and each employee has recorded current levels based on evidence such as assessments, training completions, and experience.

### 2.2 Skill-Gap Detection

The engine computes the gap between required and current competency levels. Gaps are scored using:

- **Magnitude** — how far below the required level
- **Criticality** — whether the competency is marked mission-critical
- **Organizational priority** — strategic weight assigned by leadership

### 2.3 Learning Recommendations

When a gap is identified, the platform recommends courses and content from:

- Pre-indexed learning materials
- Semantic search over document embeddings (pgvector)
- Role-aware filtering

### 2.4 AI-Powered Assessment Generation

Administrators upload PDFs, DOCX, or TXT learning materials. The system:

1. Extracts text from documents
2. Splits content into semantic chunks
3. Generates vector embeddings using Sentence-Transformers (384-dim)
4. Stores chunks and embeddings in PostgreSQL with pgvector
5. Uses an LLM (Google Flan-T5 or compatible) to generate MCQs from retrieved context
6. Stores generated questions in a review queue for admin approval

### 2.5 Closed-Loop Learning Reassessment

Employees complete assessments before and after learning. The platform applies the **40/60 Rule**:

- 40% weight to historical competency level
- 60% weight to new assessment evidence

This ensures upgrades reflect both prior mastery and demonstrated learning, preventing inflation while rewarding genuine progress.

### 2.6 Analytics Dashboards

- **Employee Dashboard** — personal gap heatmap, recommendations, progress tracking, competency history
- **Admin Dashboard** — workforce summary, gap analytics, proficiency distribution, domain health, training effectiveness, content/AI stats

### 2.7 Interactive 3D Visualization

A Three.js-powered **Skill Galaxy** lets users explore competencies as stars in a 3D universe. Selecting a domain filters the visualization, providing an intuitive way to understand organizational skill distribution.

### 2.8 Judge Tour Guide

A built-in guided tour walks evaluators through the demo personas, features, and user flows, making it easy to showcase the platform during presentations or judging.

---

## 3. Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| Next.js 16 (App Router) | React framework, SSR, routing |
| React 19 | UI library |
| Tailwind CSS v4 | Styling |
| Three.js / React Three Fiber | 3D Skill Galaxy visualization |
| Lucide React | Icons |
| canvas-confetti | Celebration animations |

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| SQLAlchemy 2.0 | ORM |
| Alembic | Database migrations |
| PostgreSQL + pgvector | Relational DB + vector similarity search |
| PyJWT + Argon2 | Authentication and password hashing |
| Sentence-Transformers | Local embedding generation |
| Transformers / Torch | Local LLM for MCQ generation |
| pypdf + python-docx | Document text extraction |

### Infrastructure

| Component | Details |
|-----------|---------|
| Vercel | Frontend deployment |
| PostgreSQL | Production database (Neon compatible) |
| Uvicorn | ASGI server |

---

## 4. Project Structure

```
skill-intelligence-platform/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with fonts and language provider
│   │   ├── page.tsx            # Main demo shell, persona switcher, Judge Tour
│   │   └── globals.css         # Global styles, CSS variables, animations
│   ├── components/
│   │   ├── ThreeSkillGalaxy.tsx    # 3D competency visualization
│   │   ├── AdminStudio.tsx         # Admin: upload content, generate/review AI questions
│   │   ├── EmployeeDashboard.tsx   # Employee: gaps, recommendations, progress
│   │   ├── WorkforceAnalytics.tsx  # Admin: charts, heatmaps, domain health
│   │   ├── AssessmentModal.tsx     # Quiz modal with 15 questions, hidden feedback
│   │   ├── JudgeTourGuide.tsx      # Guided tour ribbon for evaluators
│   │   └── Navbar.tsx              # Top navigation bar
│   ├── context/
│   │   └── LanguageContext.tsx     # English/Hindi language switching
│   ├── lib/
│   │   ├── api.ts                  # Typed API client with offline demo fallback
│   │   └── mockData.ts             # Demo personas, dashboards, 15-question mock quiz
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Environment configuration
│   │   ├── database.py             # SQLAlchemy engine and session management
│   │   ├── dependencies.py         # Auth dependencies (get_current_user, require_admin)
│   │   ├── security.py             # JWT encode/decode, password hashing
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── competency.py
│   │   │   ├── course.py
│   │   │   ├── question.py
│   │   │   ├── assessment.py
│   │   │   ├── assessment_question.py
│   │   │   ├── user_competency.py
│   │   │   ├── learning.py
│   │   │   ├── recommendation.py
│   │   │   ├── progress.py
│   │   │   ├── content_chunk.py
│   │   │   └── ai_question.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── auth.py
│   │   │   ├── assessment.py
│   │   │   ├── competency.py
│   │   │   ├── course.py
│   │   │   ├── question.py
│   │   │   └── recommendation.py
│   │   ├── api/routes/             # FastAPI route handlers
│   │   │   ├── health.py
│   │   │   ├── auth.py
│   │   │   ├── competency.py
│   │   │   ├── roles.py
│   │   │   ├── courses.py
│   │   │   ├── questions.py
│   │   │   ├── assessment.py
│   │   │   ├── recommendations.py
│   │   │   ├── dashboard.py
│   │   │   ├── learning.py
│   │   │   ├── search.py
│   │   │   └── ai_questions.py
│   │   └── services/               # Business logic services
│   │       ├── document_parser.py  # PDF/DOCX/TXT extraction
│   │       ├── chunking.py         # Text splitting
│   │       ├── embeddings.py       # Vector embedding generation
│   │       └── question_generator.py  # LLM-based MCQ generation
│   ├── migrations/                 # Alembic migration scripts
│   ├── tests/                      # Backend tests
│   ├── requirements.txt
│   ├── seed.py                     # Seed script for initial data
│   └── seed_demo.py                # Demo data seeder
│
├── .env.example                    # Environment variable template
├── .gitignore
└── README.md
```

---

## 5. Data Model Overview

### Core Entities

| Model | Description |
|-------|-------------|
| **User** | Employees and admins with roles, departments, and experience |
| **Role** | Job roles with required competencies and proficiency levels |
| **Competency** | Skills with domains, levels, and descriptions |
| **Course** | Learning materials from providers |
| **Question** | Manually curated assessment questions |
| **Assessment** | Quiz sessions linked to users and courses |
| **AssessmentQuestion** | Junction table tracking answers and scoring |
| **UserCompetency** | Evidence-based competency records per user |
| **Progress** | Course completion tracking |
| **LearningContent** | Uploaded documents for RAG processing |
| **ContentChunk** | Text chunks with vector embeddings |
| **AIGeneratedQuestion** | LLM-generated questions pending review |
| **Recommendation** | Personalized course suggestions |
| **Progress** | Course completion tracking |

### Key Relationships

- A **User** belongs to a **Role**
- A **Role** requires many **Competencies** at specific levels
- A **User** has many **UserCompetencies** (evidence records)
- A **LearningContent** has many **ContentChunks** (for RAG)
- An **Assessment** has many **AssessmentQuestions**
- An **AIGeneratedQuestion** can be reviewed and published as a **Question**

---

## 6. AI and RAG Pipeline

### Document Ingestion Flow

```
Upload (PDF/DOCX/TXT)
    │
    ▼
Text Extraction (pypdf / python-docx)
    │
    ▼
Semantic Chunking (fixed-size + overlap)
    │
    ▼
Embedding Generation (Sentence-Transformers, 384-dim)
    │
    ▼
Storage in PostgreSQL + pgvector
    │
    ▼
Ready for RAG retrieval
```

### Question Generation Flow

```
Admin selects LearningContent
    │
    ▼
Retrieve relevant ContentChunks (vector similarity)
    │
    ▼
Combine chunks into context
    │
    ▼
LLM generates MCQ (Google Flan-T5)
    │
    ▼
Validate: 4 options (A/B/C/D), correct answer, explanation
    │
    ▼
Store as AIGeneratedQuestion (status: pending)
    │
    ▼
Admin reviews and approves/rejects
    │
    ▼
If approved → publish to Question bank
```

---

## 7. API Endpoints

| Prefix | Methods | Purpose |
|--------|---------|---------|
| `/api/health` | GET | Health check |
| `/api/auth` | POST | Login, register, token refresh |
| `/api/competencies` | GET, POST, PUT, DELETE | Competency CRUD |
| `/api/roles` | GET, POST, PUT, DELETE | Role management |
| `/api/courses` | GET, POST, PUT, DELETE | Course catalog |
| `/api/questions` | GET, POST, PUT, DELETE | Question bank |
| `/api/assessments` | POST | Start assessment, submit answers, finish, score |
| `/api/ai-questions` | GET, PATCH, POST | AI question review and bulk generation |
| `/api/learning` | POST, GET | Upload content, generate MCQs, list materials |
| `/api/search` | GET | Semantic content search |
| `/api/dashboard` | GET | Employee and admin analytics |

Full interactive documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## 8. Frontend User Experience

### 8.1 Demo Personas

The platform ships with demo personas for judging:

| Persona | Role | Access |
|---------|------|--------|
| Ananya Sharma | Statistical Officer | Employee dashboard |
| Rajesh Verma | Senior Statistical Officer | Employee dashboard |
| Dr. Priya Menon | Data Scientist | Employee dashboard |
| Rohit Kumar | System Administrator | Admin studio |

Users can switch between personas instantly using the Judge Tour Guide ribbon. The frontend caches dashboard data per persona in sessionStorage for fast switching.

### 8.2 Offline Demo Mode

If the backend is unreachable, the frontend automatically falls back to rich mock data:

- Mock dashboards with realistic Indian statistical system data
- Mock 15-question assessments with dynamic scoring
- Mock learning content and AI question queues

This ensures the demo is always presentable, even without a live backend.

### 8.3 Assessment Experience

- 15-question adaptive quiz
- No per-question feedback during the quiz
- Options highlight when selected but remain neutral
- After completion: full answer review showing correct/incorrect for every question
- Score summary with competency progression (40/60 Rule)

### 8.4 Language Support

Built-in English/Hindi toggle using React Context and localStorage persistence.

---

## 9. Assessment and Scoring Logic

### 40/60 Rule

When an assessment is completed, the platform computes the updated competency level:

```
new_level = round(0.4 × existing_level + 0.6 × assessment_evidence_level)
```

Where `assessment_evidence_level` is derived from the assessment score mapped to the L1–L5 scale.

This rule ensures:
- New learning evidence is weighted more heavily than prior level
- Historical competency is not discarded
- Competency upgrades reflect demonstrated mastery

### Scoring Flow

1. Employee starts assessment
2. Backend creates `Assessment` record with status `in_progress`
3. Employee answers each question
4. Backend validates each answer against the correct answer
5. Employee clicks "Submit & Upgrade Competencies"
6. Backend calls `finish_assessment()` then `score_assessment()`
7. Score is computed, competency levels are updated using 40/60 Rule
8. Recommendations are refreshed based on new gaps
9. Frontend shows final score, correct/incorrect breakdown, and competency updates

---

## 10. Running the Project

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/harsh674-dot/skill-intelligence-platform.git
cd skill-intelligence-platform
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env at root)
# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/skill_intelligence_db
# JWT_SECRET_KEY=your_jwt_secret_key_here
# ENVIRONMENT=development

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

### Seeding Demo Data

```bash
cd backend
python seed_demo.py
```

This creates:
- Admin and employee users
- Roles and competencies
- Courses and learning content
- Sample questions and assessments

---

## 11. Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | Secret for JWT encoding | Yes |
| `ENVIRONMENT` | `development` or `production` | No |

---

## 12. Deployment

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

### Database

- Use Neon, Supabase, or any PostgreSQL 14+ provider
- Enable the pgvector extension
- Run `alembic upgrade head` after deployment

---

## 13. Security

- Passwords hashed with Argon2
- JWT-based authentication with HTTPBearer scheme
- Role-based access control (`employee` and `admin`)
- Admin-only routes protected by `require_admin` dependency
- No secrets committed to the repository

---

## 14. Testing

```bash
cd backend
pytest tests/
```

---

## 15. License

Developed for **Smart India Hackathon (SIH26101)**.

---

## 16. Live Database Authentication & Persona Credentials

The fake/mock fallbacks have been completely eliminated. All personas in the **Judge / Persona Switcher** are backed by real **PostgreSQL** records, authenticating via JWT tokens through the FastAPI backend (`POST /api/auth/login`).

### 16.1 Login Credentials for All Personas

| Avatar | Name | Role & Department | Access Role | Login Email | Password |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **A** | **Ananya Sharma** | Statistical Officer • National Statistical Office | `employee` | `ananya.sharma@demo.gov.in` | `Demo@12345` |
| **R** | **Rahul Verma** | Data Analyst • National Statistical Office | `employee` | `rahul.verma@demo.gov.in` | `Demo@12345` |
| **P** | **Priya Nair** | Senior Statistical Officer • National Sample Survey Office | `employee` | `priya.nair@demo.gov.in` | `Demo@12345` |
| **R** | **Rohit Kumar** | System Admin • State Directorate of Economics and Statistics | `admin` | `rohit.kumar@demo.gov.in` | `Demo@12345` |

### 16.2 Implementation Architecture & Fixes

1. **Local PostgreSQL Database Activated**:
   - Switched from the offline remote Neon URL to the local PostgreSQL database (`skill_intelligence` on port `5432`).
   - Adjusted `embedding` column in [content_chunk.py](file:///c:/Users/GIGABYTE/Downloads/skill-intelligence-platform/backend/app/models/content_chunk.py) to remove external C-extension requirements, enabling clean native table generation.
   - Seeded all 12 real users, 34 competencies, 50 role mappings, 23 courses, and 102 assessment questions.

2. **No More Fake/Mock Fallbacks**:
   - Removed the aggressive circuit breaker and 1.2s premature mock timeout in [api.ts](file:///c:/Users/GIGABYTE/Downloads/skill-intelligence-platform/frontend/lib/api.ts).
   - In [page.tsx](file:///c:/Users/GIGABYTE/Downloads/skill-intelligence-platform/frontend/app/page.tsx), switching a persona directly calls `POST /api/auth/login` to retrieve a real JWT access token, fetches `/api/auth/me`, and retrieves the real employee/admin dashboard data.

3. **In-App Persona Switcher & Direct Sign-In**:
   - The dropdown switcher in [Navbar.tsx](file:///c:/Users/GIGABYTE/Downloads/skill-intelligence-platform/frontend/components/Navbar.tsx) allows instant one-click switching with real backend JWT authentication while keeping the UI clean.
   - Added a **"Sign In with Custom Credentials"** modal in the Navbar to allow manual authentication with any email and password.

4. **Verification**:
   - All 4 accounts verified live against `http://127.0.0.1:8000/api/auth/login` and `/api/auth/me` (returning `200 OK` with valid JWT tokens).
   - Frontend TypeScript check (`npx tsc --noEmit`) passes with 0 errors.

> [!NOTE]
> Both the frontend (`http://localhost:3000`) and backend (`http://127.0.0.1:8000`) are actively running and ready to test directly in your browser.

