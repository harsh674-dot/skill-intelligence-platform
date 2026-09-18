import uuid
import time
import logging
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.competency import Competency, UserCompetency, RoleCompetency
from app.models.course import Course
from app.models.learning import Recommendation, Progress
from app.models.user import User
from app.models.profile import OfficialProfile, CompetencyAssessmentRecord, LearningEvent

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """
    Predictive Analytics (Section 4.4):
    Time-series/skill-forecasting on organization-wide competency data.
    
    In production this would use actual ML models on historical data.
    This implementation provides a working simulation grounded in real
    DB state that produces meaningful forecasts.
    """

    def __init__(self, db: Session):
        self.db = db

    def predict_skill_gaps(
        self,
        department: Optional[str] = None,
        timeframe_months: int = 6,
    ) -> list[dict]:
        """
        Predict emerging skill shortages.
        
        Analyzes current gaps, growth trends, and departmental
        priorities to forecast which competencies will become critical.
        """
        users = self.db.query(User).filter(User.is_active == True).all()
        if department:
            users = [u for u in users if (u.department or "").lower() == department.lower()]

        forecasts = []

        for user in users:
            if not user.job_role_id:
                continue

            role_comps = (
                self.db.query(RoleCompetency)
                .filter(RoleCompetency.role_id == user.job_role_id)
                .all()
            )

            user_comps = {
                uc.competency_id: uc.current_level
                for uc in (
                    self.db.query(UserCompetency)
                    .filter(UserCompetency.user_id == user.id)
                    .all()
                )
            }

            for rc in role_comps:
                current = user_comps.get(rc.competency_id, 1)
                gap = rc.required_level - current

                if gap <= 0:
                    continue

                # Simulate growth rate based on priority and criticality
                growth_rate = 0.05 + (rc.organizational_priority * 0.02)
                if rc.is_critical:
                    growth_rate *= 1.5

                projected_gap = max(0, gap * (1 + growth_rate * (timeframe_months / 6)))

                if projected_gap > gap * 1.1:
                    forecasts.append({
                        "user_id": str(user.id),
                        "user_name": user.full_name,
                        "department": user.department or "Unassigned",
                        "competency_id": str(rc.competency_id),
                        "current_gap": gap,
                        "projected_gap": round(float(projected_gap), 2),
                        "trend": "increasing",
                        "timeframe_months": timeframe_months,
                        "risk_level": "high" if projected_gap >= gap * 1.5 else "medium",
                        "is_critical": rc.is_critical,
                        "recommendation": (
                            "Immediate intervention recommended"
                            if rc.is_critical and projected_gap >= gap * 1.5
                            else "Monitor and schedule upskilling"
                        ),
                    })

        forecasts.sort(key=lambda x: (-x["risk_level"] == "high", -x["projected_gap"]))
        return forecasts

    def predict_course_success(
        self,
        course_id: str,
        user_id: str,
    ) -> dict:
        """
        Predict the likelihood of a user successfully completing a course.
        """
        user = self.db.get(User, user_id)
        if not user:
            return {"error": "User not found"}

        course = self.db.get(Course, course_id)
        if not course:
            return {"error": "Course not found"}

        progress = (
            self.db.query(Progress)
            .filter(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
            )
            .first()
        )

        user_comps = (
            self.db.query(UserCompetency)
            .filter(UserCompetency.user_id == user_id)
            .all()
        )
        user_levels = {uc.competency_id: uc.current_level for uc in user_comps}

        course_comps = (
            self.db.query(CourseCompetency)
            .filter(CourseCompetency.course_id == course_id)
            .all()
        )

        avg_alignment = 0.0
        if course_comps:
            alignments = []
            for cc in course_comps:
                current = user_levels.get(cc.competency_id, 1)
                alignment = min(current / cc.target_level, 1.0) if cc.target_level > 0 else 0.5
                alignments.append(alignment)
            avg_alignment = sum(alignments) / len(alignments) if alignments else 0.5

        success_probability = round(min(avg_alignment * 85 + 15, 98), 2)

        difficulty_factor = {
            "beginner": 1.0,
            "intermediate": 0.9,
            "advanced": 0.75,
        }
        factor = difficulty_factor.get(course.level or "beginner", 0.9)
        adjusted_probability = round(success_probability * factor, 2)

        estimated_days = round(
            (course.duration_minutes or 120) / 60 * (12 / max(adjusted_probability, 10)),
            1,
        )

        return {
            "course_id": course_id,
            "user_id": user_id,
            "success_probability": adjusted_probability,
            "predicted_completion_time_days": estimated_days,
            "confidence_score": round(avg_alignment, 3),
            "factors": [
                f"Skill alignment: {round(avg_alignment * 100, 1)}%",
                f"Course difficulty: {course.level or 'N/A'}",
                f"Prior progress: {'Yes' if progress else 'None'}",
            ],
        }

    def organization_skill_heatmap(self) -> dict:
        """Generate organization-wide competency heatmap data."""
        users = self.db.query(User).filter(User.is_active == True, User.job_role_id.is_not(None)).all()
        all_comps = self.db.query(Competency).filter(Competency.is_active == True).all()

        heatmap = {}
        for comp in all_comps:
            levels = []
            for user in users:
                uc = (
                    self.db.query(UserCompetency)
                    .filter(
                        UserCompetency.user_id == user.id,
                        UserCompetency.competency_id == comp.id,
                    )
                    .first()
                )
                levels.append(uc.current_level if uc else 1)

            if levels:
                heatmap[str(comp.id)] = {
                    "competency_name": comp.name,
                    "domain": comp.domain,
                    "avg_level": round(sum(levels) / len(levels), 2),
                    "min_level": min(levels),
                    "max_level": max(levels),
                    "distribution": {
                        str(l): levels.count(l) for l in range(1, 6)
                    },
                }

        return {"total_officials": len(users), "total_competencies": len(all_comps), "heatmap": heatmap}

    def predict_training_risk(
        self,
        department: Optional[str] = None,
        threshold: float = 0.3,
    ) -> list[dict]:
        """Identify users at risk of failing upcoming training."""
        users = self.db.query(User).filter(User.is_active == True).all()
        if department:
            users = [u for u in users if (u.department or "").lower() == department.lower()]

        risks = []
        for user in users:
            if not user.job_role_id:
                continue

            progress_records = (
                self.db.query(Progress)
                .filter(Progress.user_id == user.id)
                .all()
            )
            if not progress_records:
                continue

            avg_progress = sum(p.completion_percentage or 0 for p in progress_records) / len(progress_records)
            recent_events = [
                e for e in self.db.query(LearningEvent).filter(LearningEvent.profile_id == user.id).all()
                if e.event_type in ("completion", "score")
            ]
            recent_success = 0.0
            if recent_events:
                recent_success = sum((e.score or 0) for e in recent_events) / len(recent_events) / 100.0

            risk_score = max(0.0, 1.0 - (avg_progress * 0.5 + recent_success * 0.5))
            if risk_score >= threshold:
                risks.append({
                    "user_id": str(user.id),
                    "user_name": user.full_name,
                    "department": user.department or "Unassigned",
                    "risk_score": round(risk_score, 3),
                    "avg_progress": round(avg_progress, 3),
                    "recent_avg_score": round(recent_success, 3),
                    "active_courses": len(progress_records),
                    "risk_level": "high" if risk_score >= 0.6 else "medium" if risk_score >= 0.4 else "low",
                    "recommendation": (
                        "Immediate remediation required"
                        if risk_score >= 0.6
                        else "Schedule check-in and provide support"
                    ),
                })

        risks.sort(key=lambda x: -x["risk_score"])
        return risks

    def predict_retention(
        self,
        department: Optional[str] = None,
        timeframe_days: int = 90,
    ) -> dict:
        """Predict employee retention based on learning engagement patterns."""
        users = self.db.query(User).filter(User.is_active == True).all()
        if department:
            users = [u for u in users if (u.department or "").lower() == department.lower()]

        total_users = len(users)
        engaged_users = 0
        at_risk_users = 0
        user_risk_details = []

        for user in users:
            events = self.db.query(LearningEvent).filter(LearningEvent.profile_id == user.id).all()
            progress = self.db.query(Progress).filter(Progress.user_id == user.id).all()

            if not events and not progress:
                at_risk_users += 1
                user_risk_details.append({
                    "user_id": str(user.id),
                    "user_name": user.full_name,
                    "engagement_score": 0.0,
                    "reason": "No learning activity",
                })
                continue

            engagement = 0.0
            if events:
                engagement += min(len(events) / 10, 0.5)
            if progress:
                engagement += min(sum(p.completion_percentage or 0 for p in progress) / len(progress) / 100 * 0.5, 0.5)

            if engagement >= 0.3:
                engaged_users += 1
            else:
                at_risk_users += 1

            user_risk_details.append({
                "user_id": str(user.id),
                "user_name": user.full_name,
                "engagement_score": round(engagement, 3),
                "reason": "Low engagement" if engagement < 0.3 else "Active",
            })

        predicted_retention_rate = round(
            (engaged_users / max(total_users, 1)) * 100, 1
        )

        return {
            "timeframe_days": timeframe_days,
            "total_users": total_users,
            "engaged_users": engaged_users,
            "at_risk_users": at_risk_users,
            "predicted_retention_rate": predicted_retention_rate,
            "risk_distribution": {
                "high": sum(1 for d in user_risk_details if d["engagement_score"] < 0.15),
                "medium": sum(1 for d in user_risk_details if 0.15 <= d["engagement_score"] < 0.3),
                "low": sum(1 for d in user_risk_details if d["engagement_score"] >= 0.3),
            },
            "at_risk_details": sorted(user_risk_details, key=lambda x: x["engagement_score"])[:20],
        }

    def predict_role_fit(
        self,
        user_id: str,
    ) -> dict:
        """Predict how well a user fits their current role based on competency levels."""
        user = self.db.get(User, user_id)
        if not user:
            return {"error": "User not found"}

        if not user.job_role_id:
            return {"error": "User has no assigned role"}

        role_comps = (
            self.db.query(RoleCompetency)
            .filter(RoleCompetency.role_id == user.job_role_id)
            .all()
        )
        user_comps = {
            uc.competency_id: uc.current_level
            for uc in self.db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()
        }

        if not role_comps:
            return {"error": "Role has no competency requirements"}

        fit_scores = []
        for rc in role_comps:
            current = user_comps.get(rc.competency_id, 0)
            gap = rc.required_level - current
            fit = max(0.0, min(1.0, 1.0 - (gap / max(rc.required_level, 1))))
            fit_scores.append({
                "competency_id": str(rc.competency_id),
                "competency_name": self.db.get(Competency, rc.competency_id).name if self.db.get(Competency, rc.competency_id) else "Unknown",
                "required_level": rc.required_level,
                "current_level": current,
                "gap": gap,
                "fit_score": round(fit, 3),
            })

        overall_fit = round(sum(s["fit_score"] for s in fit_scores) / len(fit_scores), 3) if fit_scores else 0.0

        return {
            "user_id": user_id,
            "user_name": user.full_name,
            "current_role": user.job_role_id,
            "overall_role_fit": overall_fit,
            "fit_level": "excellent" if overall_fit >= 0.85 else "good" if overall_fit >= 0.7 else "developing" if overall_fit >= 0.5 else "poor",
            "competency_breakdown": fit_scores,
            "critical_gaps": [s for s in fit_scores if s["gap"] >= 2],
            "recommendation": (
                "Role assignment is appropriate"
                if overall_fit >= 0.75
                else "Schedule upskilling before role expansion"
                if overall_fit >= 0.5
                else "Consider role reassignment or intensive training"
            ),
        }


def predict_future_skill_gaps(db: Session, department_id: str = None) -> list:
    service = PredictiveAnalyticsService(db)
    return service.predict_skill_gaps(department_id)


def predict_training_success_rate(db: Session, course_id: str, user_id: str) -> dict:
    service = PredictiveAnalyticsService(db)
    return service.predict_course_success(course_id, user_id)
