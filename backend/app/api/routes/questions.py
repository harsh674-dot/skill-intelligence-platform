import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.question import Question
from app.models.user import User
from app.schemas.question import QuestionResponse, QuestionCreateRequest, QuestionUpdateRequest

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)


@router.get(
    "",
    response_model=list[QuestionResponse],
)
def get_questions(
    db: Session = Depends(get_db),
):
    statement = (
        select(Question)
        .where(Question.is_active.is_(True))
        .order_by(Question.created_at)
    )

    return db.scalars(statement).all()


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    data: QuestionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Create a new question."""
    from app.models.question import Question as QuestionModel

    question = QuestionModel(
        competency_id=data.competency_id,
        question_text=data.question_text,
        question_type=data.question_type,
        difficulty=data.difficulty,
        options=data.options,
        correct_answer=data.correct_answer,
        explanation=data.explanation,
        bloom_tag=data.bloom_tag,
        is_active=True,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
)
def update_question(
    question_id: uuid.UUID,
    data: QuestionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Update an existing question."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    if data.question_text is not None:
        question.question_text = data.question_text
    if data.options is not None:
        question.options = data.options
    if data.correct_answer is not None:
        question.correct_answer = data.correct_answer
    if data.explanation is not None:
        question.explanation = data.explanation
    if data.bloom_tag is not None:
        question.bloom_tag = data.bloom_tag
    if data.difficulty is not None:
        question.difficulty = data.difficulty

    db.commit()
    db.refresh(question)
    return question


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin-only: Deactivate (soft delete) a question."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    question.is_active = False
    db.commit()
