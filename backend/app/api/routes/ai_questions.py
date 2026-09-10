from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
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


@router.post("/generate")
def generate_ai_questions(
    learning_content_id: UUID,
    difficulty: str = "beginner",
    count: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Generate multiple AI MCQs from learning content.

    Questions are generated from different content chunks
    whenever enough chunks are available.
    """

    # -----------------------------------------------------
    # 1. Validate difficulty
    # -----------------------------------------------------

    allowed_difficulties = {
        "beginner",
        "intermediate",
        "advanced",
    }

    difficulty = difficulty.lower().strip()

    if difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Difficulty must be beginner, intermediate, "
                "or advanced."
            ),
        )

    # -----------------------------------------------------
    # 2. Validate count
    # -----------------------------------------------------

    if count < 1 or count > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be between 1 and 20.",
        )

    # -----------------------------------------------------
    # 3. Find content chunks
    # -----------------------------------------------------

    statement = (
        select(ContentChunk)
        .where(
            ContentChunk.learning_content_id
            == learning_content_id
        )
        .order_by(ContentChunk.chunk_index)
    )

    chunks = db.scalars(statement).all()

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No content chunks found for this learning content."
            ),
        )

    # -----------------------------------------------------
    # 4. Select chunks
    # -----------------------------------------------------
    #
    # If the document has fewer chunks than requested,
    # we generate one question per available chunk.
    #
    # If the document has enough chunks, each question
    # initially uses a different chunk.
    #
    # For very small documents, chunks are reused only after
    # every available chunk has been used.
    # -----------------------------------------------------

    selected_chunks = []

    for index in range(count):
        selected_chunks.append(
            chunks[index % len(chunks)]
        )

    # -----------------------------------------------------
    # 5. Generate questions
    # -----------------------------------------------------

    generated_questions = []
    generation_errors = []

    for index, source_chunk in enumerate(selected_chunks):

        try:
            print(
                f"Generating MCQ {index + 1}/{count} "
                f"from chunk {source_chunk.chunk_index}"
            )

            generated = generate_mcq(
                source_chunk.chunk_text,
                difficulty=difficulty,
            )

            # ---------------------------------------------
            # Basic validation
            # ---------------------------------------------

            required_fields = {
                "question_text",
                "options",
                "correct_answer",
            }

            missing_fields = required_fields - set(
                generated.keys()
            )

            if missing_fields:
                raise ValueError(
                    "Generated question is missing fields: "
                    + ", ".join(sorted(missing_fields))
                )

            options = generated.get("options")

            if not isinstance(options, dict):
                raise ValueError(
                    "Generated question options are invalid."
                )

            required_options = {"A", "B", "C", "D"}

            if not required_options.issubset(options.keys()):
                raise ValueError(
                    "Generated question must contain "
                    "options A, B, C and D."
                )

            # ---------------------------------------------
            # Create database object
            # ---------------------------------------------

            question = AIGeneratedQuestion(
                learning_content_id=learning_content_id,
                competency_id=None,
                question_text=generated["question_text"],
                question_type="mcq",
                difficulty=difficulty,
                options=options,
                correct_answer=generated["correct_answer"],
                explanation=generated.get("explanation"),
                source_chunk_ids=[
                    str(source_chunk.id)
                ],
                generation_model="google/flan-t5-base",
                status="pending",
            )

            db.add(question)

            generated_questions.append(
                question
            )

        except Exception as exc:

            error_message = (
                f"Question {index + 1} failed: {exc}"
            )

            print(error_message)

            generation_errors.append(
                error_message
            )

    # -----------------------------------------------------
    # 6. Make sure at least one question was generated
    # -----------------------------------------------------

    if not generated_questions:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": (
                    "Could not generate any valid MCQs."
                ),
                "errors": generation_errors,
            },
        )

    # -----------------------------------------------------
    # 7. Save generated questions
    # -----------------------------------------------------

    try:
        db.commit()

        for question in generated_questions:
            db.refresh(question)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "MCQs were generated but could not be saved: "
                f"{exc}"
            ),
        )

    # -----------------------------------------------------
    # 8. Return generated questions
    # -----------------------------------------------------

    return {
        "learning_content_id": str(
            learning_content_id
        ),
        "difficulty": difficulty,
        "requested_count": count,
        "generated_count": len(
            generated_questions
        ),
        "failed_count": len(
            generation_errors
        ),
        "generation_errors": generation_errors,
        "questions": [
            {
                "id": str(question.id),
                "learning_content_id": str(
                    question.learning_content_id
                ),
                "competency_id": (
                    str(question.competency_id)
                    if question.competency_id
                    else None
                ),
                "question_text": question.question_text,
                "question_type": question.question_type,
                "difficulty": question.difficulty,
                "options": question.options,
                "correct_answer": (
                    question.correct_answer
                ),
                "explanation": question.explanation,
                "source_chunk_ids": (
                    question.source_chunk_ids
                ),
                "generation_model": (
                    question.generation_model
                ),
                "status": question.status,
                "created_at": question.created_at,
                "updated_at": question.updated_at,
            }
            for question in generated_questions
        ],
    }