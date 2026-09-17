import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    analytics,
    ai_questions,
    ai_ml,
    admin,
    assessment,
    auth,
    audit,
    chatbot,
    community,
    competency,
    courses,
    dashboard,
    dpdp,
    experience_reviews,
    health,
    igot,
    jobs,
    learning,
    learning_events,
    media,
    profiles,
    questions,
    recommendations,
    roles,
    search,
    tpac,
)
from app.middleware.audit import AuditMiddleware
from app.middleware.health import HealthCheckMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


app = FastAPI(
    title="Skill Intelligence Platform API",
    description="Backend API for the Skill Intelligence Platform",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — never use wildcard "*" in production.
# Set ALLOWED_ORIGINS in the environment as a comma-separated list of origins.
# Example: ALLOWED_ORIGINS=https://skill.gov.in,https://www.skill.gov.in
# ---------------------------------------------------------------------------

_DEFAULT_DEV_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

_env_origins = os.environ.get("ALLOWED_ORIGINS", "")
_extra_origins = [o.strip() for o in _env_origins.split(",") if o.strip()]
_allowed_origins = list(dict.fromkeys(_DEFAULT_DEV_ORIGINS + _extra_origins))

app.add_middleware(
    RateLimitMiddleware,
)

app.add_middleware(
    AuditMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    HealthCheckMiddleware,
)



# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

app.include_router(
    health.router,
)

app.include_router(
    audit.router,
)

app.include_router(
    dpdp.router,
)

app.include_router(
    admin.router,
)

app.include_router(
    ai_ml.router,
)

app.include_router(
    learning_events.router,
)

app.include_router(
    media.router,
)

app.include_router(
    profiles.router,
)

app.include_router(
    competency.router,
    prefix="/api",
)

app.include_router(
    roles.router,
    prefix="/api",
)

app.include_router(
    courses.router,
    prefix="/api",
)

app.include_router(
    questions.router,
    prefix="/api",
)

app.include_router(
    assessment.router,
    prefix="/api",
)

app.include_router(
    auth.router,
    prefix="/api",
)

app.include_router(
    recommendations.router,
    prefix="/api",
)

app.include_router(
    dashboard.router,
    prefix="/api",
)

app.include_router(
    learning.router,
    prefix="/api",
)

app.include_router(
    search.router,
    prefix="/api",
)

app.include_router(
    ai_questions.router,
    prefix="/api",
)

app.include_router(
    chatbot.router,
    prefix="/api",
)

app.include_router(
    community.router,
    prefix="/api",
)

app.include_router(
    experience_reviews.router,
    prefix="/api",
)

app.include_router(
    jobs.router,
    prefix="/api",
)

app.include_router(
    igot.router,
    prefix="/api",
)

app.include_router(
    tpac.router,
    prefix="/api",
)

app.include_router(
    analytics.router,
    prefix="/api",
)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Skill Intelligence Platform API",
        "version": "1.0.0",
        "status": "running",
    }