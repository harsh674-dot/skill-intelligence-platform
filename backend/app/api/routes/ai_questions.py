from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.jobs import (
    complete_job,
    create_job,
    fail_job,
    set_job_running,
)
from app.database import SessionLocal, get_db
from app.dependencies import require_admin
from app.models.ai_question import AIGeneratedQuestion
from app.models.content_chunk import ContentChunk
from app.models.user import User
from app.services.question_generator import generate_mcq


router = APIRouter(
    prefix="/ai-questions",
    tags=["AI Questions"],
)


# =========================================================
# SCHEMAS
# =========================================================


from app.models.question import Question
from app.models.competency import Competency


class ReviewQuestionRequest(BaseModel):
    status: str = Field(
        ...,
        description="Review decision: approved or rejected",
    )
    question_text: str | None = None
    options: dict[str, str] | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    competency_id: UUID | None = None



# =========================================================
# GET ALL AI QUESTIONS
# =========================================================


@router.get("")
def get_ai_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Return all AI-generated questions.
    """

    statement = (
        select(AIGeneratedQuestion)
        .order_by(AIGeneratedQuestion.created_at.desc())
    )

    questions = db.scalars(statement).all()

    return [
        {
            "id": str(question.id),
            "learning_content_id": str(question.learning_content_id),
            "competency_id": (
                str(question.competency_id)
                if question.competency_id
                else None
            ),
            "question_text": question.question_text,
            "question_type": question.question_type,
            "difficulty": question.difficulty,
            "bloom_tag": question.bloom_tag,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "source_chunk_ids": question.source_chunk_ids,
            "generation_model": question.generation_model,
            "status": question.status,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
        }
        for question in questions
    ]


# =========================================================
# GET SINGLE AI QUESTION
# =========================================================


@router.get("/{question_id}")
def get_ai_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Return one AI-generated question.
    """

    question = db.get(
        AIGeneratedQuestion,
        question_id,
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI-generated question not found.",
        )

    return {
        "id": str(question.id),
        "learning_content_id": str(question.learning_content_id),
        "competency_id": (
            str(question.competency_id)
            if question.competency_id
            else None
        ),
        "question_text": question.question_text,
        "question_type": question.question_type,
        "difficulty": question.difficulty,
        "bloom_tag": question.bloom_tag,
        "options": question.options,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "source_chunk_ids": question.source_chunk_ids,
        "generation_model": question.generation_model,
        "status": question.status,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


# =========================================================
# REVIEW AI QUESTION
# =========================================================


@router.patch("/{question_id}/review")
def review_ai_question(
    question_id: UUID,
    payload: ReviewQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Approve or reject an AI-generated question.
    """

    new_status = payload.status.lower().strip()

    if new_status not in {"approved", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'approved' or 'rejected'.",
        )

    question = db.get(
        AIGeneratedQuestion,
        question_id,
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI-generated question not found.",
        )

    if question.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Question has already been reviewed. "
                f"Current status: {question.status}"
            ),
        )

    if payload.question_text:
        question.question_text = payload.question_text
    if payload.options:
        question.options = payload.options
    if payload.correct_answer:
        question.correct_answer = payload.correct_answer
    if payload.explanation:
        question.explanation = payload.explanation
    if payload.competency_id:
        question.competency_id = payload.competency_id

    question.status = new_status

    published_id = None
    if new_status == "approved":
        target_comp_id = question.competency_id
        if not target_comp_id:
            first_comp = db.query(Competency).filter(Competency.is_active == True).first()
            if first_comp:
                target_comp_id = first_comp.id
                question.competency_id = target_comp_id

        if target_comp_id:
            master_q = Question(
                competency_id=target_comp_id,
                question_text=question.question_text,
                question_type="mcq",
                difficulty=question.difficulty or "intermediate",
                bloom_tag=question.bloom_tag,
                options=question.options,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                is_active=True,
            )
            db.add(master_q)
            db.flush()
            published_id = str(master_q.id)

    try:
        db.commit()
        db.refresh(question)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update question status: {exc}",
        )

    return {
        "message": f"Question {new_status} successfully.",
        "id": str(question.id),
        "status": question.status,
        "published_question_id": published_id,
    }



# =========================================================
# GENERATE MULTIPLE AI QUESTIONS FROM CONTENT
# =========================================================


# ---------------------------------------------------------------------------
# Internal background worker — runs Torch generation off the event loop
# ---------------------------------------------------------------------------

def _run_generation_job(
    job_id: str,
    learning_content_id: UUID,
    difficulty: str,
    count: int,
) -> None:
    """
    Background task: generates MCQs with Flan-T5 and writes results to the
    job store.  Opens its own DB session so it doesn't share the request session.
    """
    set_job_running(job_id)
    db = SessionLocal()
    try:
        # Fetch chunks
        statement = (
            select(ContentChunk)
            .where(ContentChunk.learning_content_id == learning_content_id)
            .order_by(ContentChunk.chunk_index)
        )
        chunks = db.scalars(statement).all()

        if not chunks:
            fail_job(job_id, "No content chunks found for this learning content.")
            return

        selected_chunks = [chunks[i % len(chunks)] for i in range(count)]

        generated_questions = []
        generation_errors = []

        for index, source_chunk in enumerate(selected_chunks):
            try:
                generated = generate_mcq(
                    source_chunk.chunk_text,
                    difficulty=difficulty,
                    question_number=index + 1,
                )

                required_fields = {"question_text", "options", "correct_answer"}
                missing = required_fields - set(generated.keys())
                if missing:
                    raise ValueError("Missing fields: " + ", ".join(sorted(missing)))

                options = generated.get("options")
                if not isinstance(options, dict):
                    raise ValueError("Generated options are invalid.")
                if not {"A", "B", "C", "D"}.issubset(options.keys()):
                    raise ValueError("Options must contain A, B, C and D.")

                question = AIGeneratedQuestion(
                    learning_content_id=learning_content_id,
                    competency_id=None,
                    question_text=generated["question_text"],
                    question_type="mcq",
                    difficulty=difficulty,
                    bloom_tag=generated.get("bloom_tag"),
                    options=options,
                    correct_answer=generated["correct_answer"],
                    explanation=generated.get("explanation"),
                    source_chunk_ids=[str(source_chunk.id)],
                    generation_model="google/flan-t5-base",
                    status="pending",
                )
                db.add(question)
                generated_questions.append(question)

            except Exception as exc:
                msg = f"Question {index + 1} failed: {exc}"
                print(msg)
                generation_errors.append(msg)

        if not generated_questions:
            db.rollback()
            fail_job(job_id, "Could not generate any valid MCQs. Errors: " + "; ".join(generation_errors))
            return

        db.commit()
        for q in generated_questions:
            db.refresh(q)

        result = {
            "learning_content_id": str(learning_content_id),
            "difficulty": difficulty,
            "requested_count": count,
            "generated_count": len(generated_questions),
            "failed_count": len(generation_errors),
            "generation_errors": generation_errors,
            "questions": [
                {
                    "id": str(q.id),
                    "learning_content_id": str(q.learning_content_id),
                    "competency_id": str(q.competency_id) if q.competency_id else None,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "difficulty": q.difficulty,
                    "bloom_tag": q.bloom_tag,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "source_chunk_ids": q.source_chunk_ids,
                    "generation_model": q.generation_model,
                    "status": q.status,
                    "created_at": q.created_at,
                    "updated_at": q.updated_at,
                }
                for q in generated_questions
            ],
        }
        complete_job(job_id, result)

    except Exception as exc:
        db.rollback()
        fail_job(job_id, str(exc))
    finally:
        db.close()


@router.post("/generate", status_code=202)
def generate_ai_questions(
    learning_content_id: UUID,
    background_tasks: BackgroundTasks,
    difficulty: str = "beginner",
    count: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Enqueue AI MCQ generation from learning content.

    Returns 202 Accepted immediately with a job_id.
    Poll GET /api/jobs/{job_id} until status is 'done' or 'failed'.

    This avoids blocking the server event loop during Torch/LLM inference.
    """  # noqa: D401

    difficulty = difficulty.lower().strip()
    if difficulty not in {"beginner", "intermediate", "advanced"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Difficulty must be beginner, intermediate, or advanced.",
        )

    if count < 1 or count > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be between 1 and 20.",
        )

    # Verify that content chunks exist before enqueuing (fast DB check)
    chunk_exists = db.scalars(
        select(ContentChunk)
        .where(ContentChunk.learning_content_id == learning_content_id)
        .limit(1)
    ).first()

    if not chunk_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No content chunks found for this learning content.",
        )

    job_id = create_job()
    background_tasks.add_task(
        _run_generation_job,
        job_id=job_id,
        learning_content_id=learning_content_id,
        difficulty=difficulty,
        count=count,
    )

    return {
        "message": "MCQ generation enqueued. Poll the job endpoint for results.",
        "job_id": job_id,
        "learning_content_id": str(learning_content_id),
        "difficulty": difficulty,
        "requested_count": count,
        "poll_url": f"/api/jobs/{job_id}",
    }