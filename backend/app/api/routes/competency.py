from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.competency import Competency
from app.schemas.competency import CompetencyResponse

router = APIRouter(
    prefix="/competencies",
    tags=["Competencies"],
)


@router.get(
    "",
    response_model=list[CompetencyResponse],
)
def get_competencies(
    db: Session = Depends(get_db),
):
    statement = (
        select(Competency)
        .where(Competency.is_active.is_(True))
        .order_by(Competency.name)
    )

    return db.scalars(statement).all()