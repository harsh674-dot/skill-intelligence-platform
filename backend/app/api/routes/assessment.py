import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.models.assessment import Assessment
from app.models.assessment_question import (
    AssessmentQuestion,
)
from app.models.competency import (
    Competency,
    RoleCompetency,
    UserCompetency,
)
from app.models.course import CourseCompetency
from app.models.question import (
    Answer,
    Question,
)
from app.models.user import User

from app.schemas.assessment import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
)

from app.services.recommendation_engine import (
    refresh_recommendations,
)


router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


PROFICIENCY_LABELS = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert",
}


# =========================================================
# HELPER — ACCURACY TO EVIDENCE LEVEL
# =========================================================

def evidence_to_level(
    accuracy: float,
) -> int:

    if accuracy <= 20:
        return 1

    if accuracy <= 40:
        return 2

    if accuracy <= 60:
        return 3

    if accuracy <= 80:
        return 4

    return 5


# =========================================================
# HELPER — PHASE 5 COMPETENCY COMBINATION RULE
# =========================================================

def combine_competency_level(
    previous_level: int,
    evidence_level: int,
) -> int:
    """
    Phase 5 documented rule:

        Updated Level =
            40% previous competency
            +
            60% new assessment evidence

    New learning evidence receives more weight than
    historical evidence.

    Result is rounded using normal half-up rounding
    and constrained to levels 1..5.
    """

    value = (
        Decimal(previous_level)
        * Decimal("0.40")
        +
        Decimal(evidence_level)
        * Decimal("0.60")
    )

    result = int(
        value.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    return max(
        1,
        min(result, 5),
    )


# =========================================================
# HELPER — PRIORITY
# =========================================================

def calculate_priority(
    role_competency: RoleCompetency,
    gap: int,
) -> int:

    if gap <= 0:
        return 0

    criticality_weight = (
        2
        if role_competency.is_critical
        else 0
    )

    return (
        (gap * 2)
        + criticality_weight
        + role_competency.organizational_priority
    )


# =========================================================
# 30. BUILD QUIZ ATTEMPT FLOW
# =========================================================

@router.post(
    "/start",
    status_code=status.HTTP_201_CREATED,
)
def start_assessment(
    assessment_type: str = "initial",
    question_count: int = Query(
        10,
        ge=1,
        le=50,
    ),
    course_id: uuid.UUID | None = None,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    if assessment_type not in {
        "initial",
        "learning",
        "reassessment",
    }:
        raise HTTPException(
            status_code=400,
            detail="Invalid assessment type",
        )

    if (
        assessment_type in {
            "learning",
            "reassessment",
        }
        and not current_user.job_role_id
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "User does not have a job role assigned"
            ),
        )

    # -----------------------------------------------------
    # Create assessment
    # -----------------------------------------------------

    assessment = Assessment(
        user_id=current_user.id,
        assessment_type=assessment_type,
        status="in_progress",
    )

    db.add(assessment)
    db.flush()

    # -----------------------------------------------------
    # Determine target competencies
    # -----------------------------------------------------

    competency_ids = []

    if assessment_type in {
        "learning",
        "reassessment",
    }:

        # If quiz is opened from a recommended course,
        # target that course's competencies first.
        if course_id:

            competency_ids = list(
                db.scalars(
                    select(
                        CourseCompetency.competency_id
                    ).where(
                        CourseCompetency.course_id
                        == course_id
                    )
                ).all()
            )

        # Otherwise target highest-priority gaps.
        if not competency_ids:

            role_competencies = db.scalars(
                select(RoleCompetency).where(
                    RoleCompetency.role_id
                    == current_user.job_role_id
                )
            ).all()

            ranked_competencies = []

            for role_competency in (
                role_competencies
            ):

                user_competency = db.scalar(
                    select(UserCompetency).where(
                        UserCompetency.user_id
                        == current_user.id,
                        UserCompetency.competency_id
                        == role_competency.competency_id,
                    )
                )

                current_level = (
                    user_competency.current_level
                    if user_competency
                    else 1
                )

                gap = max(
                    role_competency.required_level
                    - current_level,
                    0,
                )

                if gap > 0:

                    priority = calculate_priority(
                        role_competency,
                        gap,
                    )

                    ranked_competencies.append(
                        (
                            priority,
                            role_competency.competency_id,
                        )
                    )

            ranked_competencies.sort(
                reverse=True
            )

            competency_ids = [
                competency_id
                for _, competency_id
                in ranked_competencies
            ]

    # -----------------------------------------------------
    # Select questions
    # -----------------------------------------------------

    question_query = select(
        Question
    ).where(
        Question.is_active.is_(True)
    )

    if competency_ids:

        question_query = question_query.where(
            Question.competency_id.in_(
                competency_ids
            )
        )

    questions = db.scalars(
        question_query
        .order_by(func.random())
        .limit(question_count)
    ).all()

    if not questions:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=(
                "No suitable quiz questions found."
            ),
        )

    # -----------------------------------------------------
    # Attach questions to assessment
    # -----------------------------------------------------

    for question in questions:

        db.add(
            AssessmentQuestion(
                assessment_id=assessment.id,
                question_id=question.id,
            )
        )

    db.commit()
    db.refresh(assessment)

    return {
        "message": (
            "Assessment started successfully"
        ),
        "assessment_id": assessment.id,
        "assessment_type": (
            assessment.assessment_type
        ),
        "status": assessment.status,
        "total_questions": len(questions),
        "questions": [
            {
                "id": question.id,
                "competency_id": (
                    question.competency_id
                ),
                "question_text": (
                    question.question_text
                ),
                "question_type": (
                    question.question_type
                ),
                "difficulty": question.difficulty,
                "options": question.options,
                "correct_answer": question.correct_answer,
            }
            for question in questions
        ],
    }


# =========================================================
# SUBMIT ANSWER
# =========================================================

@router.post(
    "/{assessment_id}/answers",
    response_model=AnswerSubmitResponse,
)
def submit_answer(
    assessment_id: uuid.UUID,
    request: AnswerSubmitRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "in_progress":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment is not in progress"
            ),
        )

    # IMPORTANT:
    # User can only answer questions assigned to
    # this particular assessment.
    assigned_question = db.scalar(
        select(AssessmentQuestion).where(
            AssessmentQuestion.assessment_id
            == assessment_id,
            AssessmentQuestion.question_id
            == request.question_id,
        )
    )

    if not assigned_question:

        raise HTTPException(
            status_code=400,
            detail=(
                "Question is not part of this assessment"
            ),
        )

    question = db.scalar(
        select(Question).where(
            Question.id == request.question_id,
            Question.is_active.is_(True),
        )
    )

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    selected_answer = (
        request.selected_answer.strip()
    )

    correct_answer = (
        question.correct_answer.strip()
    )

    correct_option_text = str(
        (question.options or {}).get(
            correct_answer,
            "",
        )
    ).strip()

    is_correct = (
        selected_answer.casefold()
        == correct_answer.casefold()
        or
        selected_answer.casefold()
        == correct_option_text.casefold()
    )

    score = 1 if is_correct else 0

    existing_answer = db.scalar(
        select(Answer).where(
            Answer.assessment_id
            == assessment_id,
            Answer.question_id
            == request.question_id,
        )
    )

    if existing_answer:

        existing_answer.selected_answer = (
            selected_answer
        )

        existing_answer.is_correct = (
            is_correct
        )

        existing_answer.score = score

        answer = existing_answer

    else:

        answer = Answer(
            assessment_id=assessment_id,
            question_id=request.question_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            score=score,
        )

        db.add(answer)

    db.commit()
    db.refresh(answer)

    return AnswerSubmitResponse(
        answer_id=answer.id,
        assessment_id=assessment_id,
        question_id=question.id,
        selected_answer=(
            answer.selected_answer
        ),
        saved=True,
        is_correct=is_correct,
        explanation=question.explanation,
    )



# =========================================================
# FINISH ASSESSMENT
# =========================================================

@router.post(
    "/{assessment_id}/finish",
)
def finish_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "in_progress":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment is not in progress"
            ),
        )

    # Only questions assigned to this assessment.
    question_ids = list(
        db.scalars(
            select(
                AssessmentQuestion.question_id
            ).where(
                AssessmentQuestion.assessment_id
                == assessment_id
            )
        ).all()
    )

    answers = db.scalars(
        select(Answer).where(
            Answer.assessment_id
            == assessment_id
        )
    ).all()

    total_questions = len(question_ids)

    total_answered = len(answers)

    correct_answers = sum(
        1
        for answer in answers
        if answer.is_correct
    )

    score = (
        (
            correct_answers
            / total_questions
        )
        * 100
        if total_questions
        else 0
    )

    assessment.score = score

    assessment.status = "completed"

    assessment.completed_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(assessment)

    return {
        "message": (
            "Assessment completed successfully"
        ),
        "assessment_id": assessment.id,
        "assessment_type": (
            assessment.assessment_type
        ),
        "status": assessment.status,
        "total_questions": total_questions,
        "total_answered": total_answered,
        "unanswered": (
            total_questions
            - total_answered
        ),
        "correct_answers": correct_answers,
        "score": round(score, 2),
    }


# =========================================================
# 31 + 32 + 33 + 34
# SCORE POST-LEARNING ASSESSMENT
# UPDATE COMPETENCY
# RECALCULATE GAPS
# REFRESH RECOMMENDATIONS
# =========================================================

@router.post(
    "/{assessment_id}/score",
)
def score_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment must be completed "
                "before scoring"
            ),
        )

    answers = db.scalars(
        select(Answer).where(
            Answer.assessment_id
            == assessment_id
        )
    ).all()

    if not answers:

        raise HTTPException(
            status_code=400,
            detail=(
                "No answers found for this assessment"
            ),
        )

    # -----------------------------------------------------
    # Group answers by competency
    # -----------------------------------------------------

    competency_stats = {}

    for answer in answers:

        question = db.get(
            Question,
            answer.question_id,
        )

        if not question:
            continue

        stats = competency_stats.setdefault(
            question.competency_id,
            {
                "total": 0,
                "correct": 0,
            },
        )

        stats["total"] += 1

        if answer.is_correct:
            stats["correct"] += 1

    results = []

    # This gets persisted into Assessment.
    before_after_snapshot = []

    # -----------------------------------------------------
    # Process every competency
    # -----------------------------------------------------

    for competency_id, stats in (
        competency_stats.items()
    ):

        total = stats["total"]

        correct = stats["correct"]

        accuracy = (
            correct / total
        ) * 100

        evidence_level = evidence_to_level(
            accuracy
        )

        # -------------------------------------------------
        # Existing competency
        # -------------------------------------------------

        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id
                == current_user.id,
                UserCompetency.competency_id
                == competency_id,
            )
        )

        previous_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        # -------------------------------------------------
        # Role requirement
        # -------------------------------------------------

        role_competency = db.scalar(
            select(RoleCompetency).where(
                RoleCompetency.role_id
                == current_user.job_role_id,
                RoleCompetency.competency_id
                == competency_id,
            )
        )

        required_level = (
            role_competency.required_level
            if role_competency
            else previous_level
        )

        gap_before = max(
            required_level
            - previous_level,
            0,
        )

        priority_before = (
            calculate_priority(
                role_competency,
                gap_before,
            )
            if role_competency
            else 0
        )

        # -------------------------------------------------
        # PHASE 5 COMBINATION RULE
        # -------------------------------------------------

        if assessment.assessment_type in {
            "learning",
            "reassessment",
        }:

            updated_level = (
                combine_competency_level(
                    previous_level,
                    evidence_level,
                )
            )

        else:

            # Initial assessment establishes baseline.
            updated_level = evidence_level

        # -------------------------------------------------
        # Save updated competency
        # -------------------------------------------------

        if user_competency:

            user_competency.current_level = (
                updated_level
            )

            user_competency.source = (
                "assessment"
            )

            user_competency.last_assessed_at = (
                datetime.now(timezone.utc)
            )

        else:

            user_competency = UserCompetency(
                user_id=current_user.id,
                competency_id=competency_id,
                current_level=updated_level,
                source="assessment",
                last_assessed_at=(
                    datetime.now(timezone.utc)
                ),
            )

            db.add(user_competency)

        # -------------------------------------------------
        # New gap + priority
        # -------------------------------------------------

        gap_after = max(
            required_level
            - updated_level,
            0,
        )

        priority_after = (
            calculate_priority(
                role_competency,
                gap_after,
            )
            if role_competency
            else 0
        )

        competency = db.get(
            Competency,
            competency_id,
        )

        competency_name = (
            competency.name
            if competency
            else str(competency_id)
        )

        # -------------------------------------------------
        # IMPORTANT:
        # JSONB cannot serialize Python UUID objects.
        # Store competency_id as a string.
        # -------------------------------------------------

        result = {
            "competency_id": str(
                competency_id
            ),

            "competency_name": competency_name,

            "total_questions": total,

            "correct_answers": correct,

            "accuracy": round(
                accuracy,
                2,
            ),

            "previous_level": (
                previous_level
            ),

            "evidence_level": (
                evidence_level
            ),

            "updated_level": (
                updated_level
            ),

            "proficiency": (
                PROFICIENCY_LABELS[
                    updated_level
                ]
            ),

            "improvement": (
                updated_level
                - previous_level
            ),

            "required_level": (
                required_level
            ),

            "gap_before": (
                gap_before
            ),

            "gap_after": (
                gap_after
            ),

            "priority_before": (
                priority_before
            ),

            "priority_after": (
                priority_after
            ),

            "next_learning_target": (
                required_level
                if gap_after > 0
                else "Maintain current level"
            ),
        }

        results.append(result)

        before_after_snapshot.append(
            result
        )

    # -----------------------------------------------------
    # Persist before/after result
    # -----------------------------------------------------

    assessment.competency_results = (
        before_after_snapshot
    )

    db.commit()

    from app.api.routes.dashboard import invalidate_dashboard_cache
    invalidate_dashboard_cache(current_user.id)

    # -----------------------------------------------------
    # 33 + 34
    #
    # Current UserCompetency values are now updated.
    # Recalculate recommendations using the new gaps.
    # -----------------------------------------------------

    recommendation_refresh = (
        refresh_recommendations(
            db,
            current_user,
        )
    )

    total_q = sum(r["total_questions"] for r in results) if results else len(answers)
    total_corr = sum(r["correct_answers"] for r in results) if results else sum(1 for a in answers if a.is_correct)
    overall_acc = round((total_corr / total_q * 100), 2) if total_q > 0 else 0.0

    competency_updates = [
        {
            "competency_id": r["competency_id"],
            "competency_name": r["competency_name"],
            "previous_level": r["previous_level"],
            "evidence_level": r["evidence_level"],
            "updated_level": r["updated_level"],
            "previous_gap": r["gap_before"],
            "new_gap": r["gap_after"],
        }
        for r in results
    ]

    return {
        "message": (
            "Post-learning assessment "
            "scored successfully"
        ),
        "assessment_id": assessment_id,
        "assessment_type": (
            assessment.assessment_type
        ),
        "combination_rule": (
            "40% previous competency + "
            "60% new assessment evidence"
        ),
        "total_questions": total_q,
        "correct_answers": total_corr,
        "accuracy": overall_acc,
        "overall_score": overall_acc,
        "competency_updates": competency_updates,
        "results": results,
        "recommendations_refreshed": (
            recommendation_refresh
        ),
        "refreshed_recommendations_count": len(recommendation_refresh) if isinstance(recommendation_refresh, list) else 0,
    }


# =========================================================
# 35. BEFORE / AFTER PROGRESS
# =========================================================

@router.get(
    "/{assessment_id}/progress",
)
def assessment_progress(
    assessment_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment must be completed first"
            ),
        )

    results = (
        assessment.competency_results
        or []
    )

    improved = [
        result
        for result in results
        if result.get(
            "improvement",
            0,
        ) > 0
    ]

    unchanged = [
        result
        for result in results
        if result.get(
            "improvement",
            0,
        ) == 0
    ]

    declined = [
        result
        for result in results
        if result.get(
            "improvement",
            0,
        ) < 0
    ]

    remaining_gaps = [
        result
        for result in results
        if result.get(
            "gap_after",
            0,
        ) > 0
    ]

    remaining_gaps.sort(
        key=lambda result: (
            -result.get(
                "priority_after",
                0,
            ),
            -result.get(
                "gap_after",
                0,
            ),
        )
    )

    next_learning_target = (
        remaining_gaps[0]
        if remaining_gaps
        else None
    )

    return {
        "assessment_id": assessment.id,

        "assessment_type": (
            assessment.assessment_type
        ),

        "overall_score": (
            float(assessment.score)
            if assessment.score is not None
            else None
        ),

        "competencies_improved": len(
            improved
        ),

        "competencies_unchanged": len(
            unchanged
        ),

        "competencies_declined": len(
            declined
        ),

        "next_learning_target": (
            next_learning_target
        ),

        "before_after": results,
    }


# =========================================================
# 33. RECALCULATE GAPS
# =========================================================

@router.get(
    "/{assessment_id}/gaps",
)
def calculate_skill_gaps(
    assessment_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment must be completed "
                "before calculating skill gaps"
            ),
        )

    if not current_user.job_role_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "User does not have a job role assigned"
            ),
        )

    role_competencies = db.scalars(
        select(RoleCompetency).where(
            RoleCompetency.role_id
            == current_user.job_role_id
        )
    ).all()

    gaps = []

    for role_competency in (
        role_competencies
    ):

        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id
                == current_user.id,
                UserCompetency.competency_id
                == role_competency.competency_id,
            )
        )

        current_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        required_level = (
            role_competency.required_level
        )

        gap = max(
            required_level
            - current_level,
            0,
        )

        gaps.append(
            {
                "competency_id": (
                    role_competency.competency_id
                ),
                "required_level": (
                    required_level
                ),
                "current_level": (
                    current_level
                ),
                "gap": gap,
                "is_critical": (
                    role_competency.is_critical
                ),
            }
        )

    # -----------------------------------------------------
    # UUID-safe sorting
    # -----------------------------------------------------

    gaps.sort(
        key=lambda item: (
            -item["gap"],
            str(item["competency_id"]),
        )
    )

    return {
        "message": (
            "Skill gaps calculated successfully"
        ),
        "assessment_id": assessment_id,
        "role_id": current_user.job_role_id,
        "gaps": gaps,
    }


# =========================================================
# PRIORITY ENGINE
# =========================================================

@router.get(
    "/{assessment_id}/priority",
)
def calculate_priorities(
    assessment_id: uuid.UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    if assessment.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Assessment must be completed "
                "before calculating priorities"
            ),
        )

    if not current_user.job_role_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "User does not have a job role assigned"
            ),
        )

    role_competencies = db.scalars(
        select(RoleCompetency).where(
            RoleCompetency.role_id
            == current_user.job_role_id
        )
    ).all()

    priorities = []

    for role_competency in (
        role_competencies
    ):

        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id
                == current_user.id,
                UserCompetency.competency_id
                == role_competency.competency_id,
            )
        )

        current_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        required_level = (
            role_competency.required_level
        )

        gap = max(
            required_level
            - current_level,
            0,
        )

        score = calculate_priority(
            role_competency,
            gap,
        )

        priorities.append(
            {
                "competency_id": (
                    role_competency.competency_id
                ),
                "required_level": (
                    required_level
                ),
                "current_level": (
                    current_level
                ),
                "gap": gap,
                "is_critical": (
                    role_competency.is_critical
                ),
                "organizational_priority": (
                    role_competency
                    .organizational_priority
                ),
                "priority_score": score,
            }
        )

    priorities.sort(
        key=lambda item: (
            -item["priority_score"],
            -item["gap"],
        )
    )

    return {
        "message": (
            "Priority scoring completed successfully"
        ),
        "assessment_id": assessment_id,
        "role_id": current_user.job_role_id,
        "priorities": priorities,
    }