from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
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


@app.get("/")
def root():
    return {
        "message": "Skill Intelligence Platform API",
        "version": "1.0.0",
        "status": "running",
    }