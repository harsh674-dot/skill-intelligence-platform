from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user, require_admin_or_manager
from app.models.user import User
from app.models.experience_review import ExperienceReview
from app.schemas.experience_review import (
    ExperienceReviewCreate,
    ExperienceReviewResponse,
    CategoryAggregation,
    ExperienceReviewAggregatedResponse,
)

router = APIRouter(
    prefix="/experience-reviews",
    tags=["experience-reviews"],
)


def _to_review_response(review: ExperienceReview) -> ExperienceReviewResponse:
    user_role = review.user.designation or review.user.access_role if review.user else "Employee"
    user_name = review.user.full_name if review.user else "Anonymous"
    return ExperienceReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=user_name,
        user_role=user_role,
        category=review.category,
        rating=review.rating,
        comments=review.comments,
        created_at=review.created_at,
    )


@router.post("", response_model=ExperienceReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_experience_review(
    payload: ExperienceReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit an employee experience review for Platform, Training Program, or Onboarding.
    Accessible to all authenticated users.
    """
    review = ExperienceReview(
        user_id=current_user.id,
        category=payload.category,
        rating=payload.rating,
        comments=payload.comments.strip() if payload.comments else None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return _to_review_response(review)


@router.get("/my", response_model=list[ExperienceReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View reviews submitted by the currently logged-in user.
    """
    reviews = (
        db.query(ExperienceReview)
        .filter(ExperienceReview.user_id == current_user.id)
        .order_by(ExperienceReview.created_at.desc())
        .all()
    )
    return [_to_review_response(r) for r in reviews]


@router.get("/aggregated", response_model=ExperienceReviewAggregatedResponse)
def get_aggregated_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """
    View aggregated experience telemetry (averages per category, star distribution, recent feedback).
    Restricted to Admin and Manager roles.
    """
    reviews = db.query(ExperienceReview).order_by(ExperienceReview.created_at.desc()).all()

    total_reviews = len(reviews)
    if total_reviews == 0:
        return ExperienceReviewAggregatedResponse(
            overall_average=0.0,
            total_reviews=0,
            categories=[
                CategoryAggregation(
                    category="platform",
                    average_rating=0.0,
                    total_reviews=0,
                    distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                ),
                CategoryAggregation(
                    category="training_program",
                    average_rating=0.0,
                    total_reviews=0,
                    distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                ),
                CategoryAggregation(
                    category="onboarding",
                    average_rating=0.0,
                    total_reviews=0,
                    distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                ),
            ],
            recent_reviews=[],
        )

    overall_avg = round(sum(r.rating for r in reviews) / total_reviews, 2)

    cat_groups = defaultdict(list)
    for r in reviews:
        cat_groups[r.category].append(r)

    categories_result = []
    for cat in ["platform", "training_program", "onboarding"]:
        cat_reviews = cat_groups[cat]
        count = len(cat_reviews)
        avg = round(sum(r.rating for r in cat_reviews) / count, 2) if count > 0 else 0.0
        dist = {str(star): sum(1 for r in cat_reviews if r.rating == star) for star in range(1, 6)}
        categories_result.append(
            CategoryAggregation(
                category=cat,
                average_rating=avg,
                total_reviews=count,
                distribution=dist,
            )
        )

    recent_reviews = [_to_review_response(r) for r in reviews[:10]]

    return ExperienceReviewAggregatedResponse(
        overall_average=overall_avg,
        total_reviews=total_reviews,
        categories=categories_result,
        recent_reviews=recent_reviews,
    )


@router.get("", response_model=list[ExperienceReviewResponse])
def list_all_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """
    List all individual reviews for institutional auditing.
    Restricted to Admin and Manager roles.
    """
    reviews = db.query(ExperienceReview).order_by(ExperienceReview.created_at.desc()).all()
    return [_to_review_response(r) for r in reviews]
