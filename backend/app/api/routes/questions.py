from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionResponse

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