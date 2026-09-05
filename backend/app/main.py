from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    competency,
    courses,
    health,
    questions,
    roles,
)

app = FastAPI(
    title="Skill Intelligence Platform API",
    description="Backend API for the Skill Intelligence Platform",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

# Health
app.include_router(
    health.router,
)


# Competencies
app.include_router(
    competency.router,
    prefix="/api",
)


# Roles
app.include_router(
    roles.router,
    prefix="/api",
)


# Courses
app.include_router(
    courses.router,
    prefix="/api",
)


# Questions
app.include_router(
    questions.router,
    prefix="/api",
)


# Authentication
app.include_router(
    auth.router,
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