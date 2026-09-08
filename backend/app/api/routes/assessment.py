import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.assessment import Assessment
from app.models.competency import RoleCompetency, UserCompetency
from app.models.question import Answer, Question
from app.models.user import User
from app.schemas.assessment import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
)


router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


@router.post(
    "/start",
    status_code=status.HTTP_201_CREATED,
)
def start_assessment(
    assessment_type: str = "initial",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if assessment_type not in {
        "initial",
        "learning",
        "reassessment",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assessment type",
        )

    assessment = Assessment(
        user_id=current_user.id,
        assessment_type=assessment_type,
        status="in_progress",
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "message": "Assessment started successfully",
        "assessment_id": assessment.id,
        "assessment_type": assessment.assessment_type,
        "status": assessment.status,
    }


@router.post(
    "/{assessment_id}/answers",
    response_model=AnswerSubmitResponse,
)
def submit_answer(
    assessment_id: uuid.UUID,
    request: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the assessment belongs to the logged-in user
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Assessment must still be in progress
    if assessment.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not in progress",
        )

    # Check that the question exists and is active
    question = db.scalar(
        select(Question).where(
            Question.id == request.question_id,
            Question.is_active.is_(True),
        )
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    # Check whether this question already has an answer
    existing_answer = db.scalar(
        select(Answer).where(
            Answer.assessment_id == assessment_id,
            Answer.question_id == request.question_id,
        )
    )

    # ---------------------------------------------------------
    # Determine whether the submitted answer is correct
    # ---------------------------------------------------------
    selected_answer = request.selected_answer.strip()
    correct_answer = question.correct_answer.strip()

    # The database stores the correct option key.
    # Example:
    #   correct_answer = "B"
    #
    # The question options may be:
    #   {
    #       "A": "Mean",
    #       "B": "Median",
    #       "C": "Mode"
    #   }
    #
    # The user may submit either:
    #   "B"
    # or:
    #   "Median"
    correct_option_text = str(
        (question.options or {}).get(correct_answer, "")
    ).strip()

    is_correct = (
        selected_answer.casefold() == correct_answer.casefold()
        or selected_answer.casefold()
        == correct_option_text.casefold()
    )

    score = 1 if is_correct else 0

    # ---------------------------------------------------------
    # Save or update answer
    # ---------------------------------------------------------
    if existing_answer:
        # Update existing answer
        existing_answer.selected_answer = selected_answer
        existing_answer.is_correct = is_correct
        existing_answer.score = score

        answer = existing_answer

    else:
        # Create new answer
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
        selected_answer=answer.selected_answer,
        saved=True,
    )


@router.post(
    "/{assessment_id}/finish",
)
def finish_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the assessment belonging to the logged-in user
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Assessment must still be in progress
    if assessment.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment is not in progress",
        )

    # Get all active questions
    questions = db.scalars(
        select(Question).where(
            Question.is_active.is_(True)
        )
    ).all()

    # Get submitted answers
    answers = db.scalars(
        select(Answer).where(
            Answer.assessment_id == assessment_id
        )
    ).all()

    # Count correct submitted answers
    correct_answers = sum(
        1 for answer in answers if answer.is_correct
    )

    total_questions = len(questions)
    total_answered = len(answers)

    # Unanswered questions contribute 0 to final score
    score = (
        (correct_answers / total_questions) * 100
        if total_questions > 0
        else 0
    )

    # Update assessment
    assessment.score = score
    assessment.status = "completed"

    db.commit()
    db.refresh(assessment)

    return {
        "message": "Assessment completed successfully",
        "assessment_id": assessment.id,
        "status": assessment.status,
        "total_questions": total_questions,
        "total_answered": total_answered,
        "unanswered": total_questions - total_answered,
        "correct_answers": correct_answers,
        "score": round(score, 2),
    }


@router.post(
    "/{assessment_id}/score",
)
def score_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find the assessment belonging to the logged-in user
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Scoring is allowed only after the assessment is completed
    if assessment.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment must be completed before scoring",
        )

    # Get all answers for this assessment
    answers = db.scalars(
        select(Answer).where(
            Answer.assessment_id == assessment_id
        )
    ).all()

    if not answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers found for this assessment",
        )

    # Group answers by competency
    competency_stats = {}

    for answer in answers:
        question = db.get(
            Question,
            answer.question_id,
        )

        if not question:
            continue

        competency_id = question.competency_id

        if competency_id not in competency_stats:
            competency_stats[competency_id] = {
                "total": 0,
                "correct": 0,
            }

        competency_stats[competency_id]["total"] += 1

        if answer.is_correct:
            competency_stats[competency_id]["correct"] += 1

    results = []

    for competency_id, stats in competency_stats.items():
        total = stats["total"]
        correct = stats["correct"]

        accuracy = (correct / total) * 100

        # Deterministic accuracy -> proficiency level
        if accuracy <= 20:
            level = 1
            proficiency = "Beginner"

        elif accuracy <= 40:
            level = 2
            proficiency = "Basic"

        elif accuracy <= 60:
            level = 3
            proficiency = "Intermediate"

        elif accuracy <= 80:
            level = 4
            proficiency = "Advanced"

        else:
            level = 5
            proficiency = "Expert"

        # Find user's existing competency record
        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id == current_user.id,
                UserCompetency.competency_id == competency_id,
            )
        )

        if user_competency:
            # Update existing competency level
            user_competency.current_level = level
            user_competency.source = "assessment"
            user_competency.last_assessed_at = (
                datetime.now(timezone.utc)
            )

        else:
            # Create competency record if it doesn't exist
            user_competency = UserCompetency(
                user_id=current_user.id,
                competency_id=competency_id,
                current_level=level,
                source="assessment",
                last_assessed_at=datetime.now(timezone.utc),
            )

            db.add(user_competency)

        results.append(
            {
                "competency_id": competency_id,
                "total_questions": total,
                "correct_answers": correct,
                "accuracy": round(accuracy, 2),
                "current_level": level,
                "proficiency": proficiency,
            }
        )

    db.commit()

    return {
        "message": "Competency scoring completed successfully",
        "assessment_id": assessment_id,
        "results": results,
    }


@router.get(
    "/{assessment_id}/gaps",
)
def calculate_skill_gaps(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the assessment belongs to the logged-in user
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Assessment should be completed before calculating gaps
    if assessment.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Assessment must be completed "
                "before calculating skill gaps"
            ),
        )

    # User must have a job role
    if not current_user.job_role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a job role assigned",
        )

    # Get required competency levels for user's role
    role_competencies = db.scalars(
        select(RoleCompetency).where(
            RoleCompetency.role_id
            == current_user.job_role_id
        )
    ).all()

    gaps = []

    for role_competency in role_competencies:

        # Get user's current competency level
        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id == current_user.id,
                UserCompetency.competency_id
                == role_competency.competency_id,
            )
        )

        # If no assessment evidence exists,
        # use Beginner (Level 1)
        current_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        required_level = role_competency.required_level

        # Skill gap = required - current
        gap = max(
            required_level - current_level,
            0,
        )

        gaps.append(
            {
                "competency_id": role_competency.competency_id,
                "required_level": required_level,
                "current_level": current_level,
                "gap": gap,
                "is_critical": role_competency.is_critical,
            }
        )

    return {
        "message": "Skill gaps calculated successfully",
        "assessment_id": assessment_id,
        "role_id": current_user.job_role_id,
        "gaps": gaps,
    }


@router.get(
    "/{assessment_id}/priority",
)
def calculate_priorities(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the assessment belongs to the logged-in user
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Assessment must be completed
    if assessment.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Assessment must be completed "
                "before calculating priorities"
            ),
        )

    # User must have a job role
    if not current_user.job_role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a job role assigned",
        )

    # Get role competency requirements
    role_competencies = db.scalars(
        select(RoleCompetency).where(
            RoleCompetency.role_id
            == current_user.job_role_id
        )
    ).all()

    priorities = []

    for role_competency in role_competencies:

        # Get user's current competency level
        user_competency = db.scalar(
            select(UserCompetency).where(
                UserCompetency.user_id == current_user.id,
                UserCompetency.competency_id
                == role_competency.competency_id,
            )
        )

        # Default to Beginner if no assessment evidence
        current_level = (
            user_competency.current_level
            if user_competency
            else 1
        )

        required_level = role_competency.required_level

        # Calculate skill gap
        gap = max(
            required_level - current_level,
            0,
        )

        # Criticality weight
        criticality_weight = (
            2 if role_competency.is_critical else 0
        )

        # Organizational priority
        organizational_priority = (
            role_competency.organizational_priority
        )

        # Final priority score
        priority_score = (
            (gap * 2)
            + criticality_weight
            + organizational_priority
        )

        priorities.append(
            {
                "competency_id": role_competency.competency_id,
                "required_level": required_level,
                "current_level": current_level,
                "gap": gap,
                "is_critical": role_competency.is_critical,
                "organizational_priority": (
                    organizational_priority
                ),
                "priority_score": priority_score,
            }
        )

    # Highest priority first
    priorities.sort(
        key=lambda item: item["priority_score"],
        reverse=True,
    )

    return {
        "message": "Priority scoring completed successfully",
        "assessment_id": assessment_id,
        "role_id": current_user.job_role_id,
        "priorities": priorities,
    }