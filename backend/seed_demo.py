import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select, func

from app.database import SessionLocal
from app.models.user import User
from app.models.competency import Competency, UserCompetency, RoleCompetency
from app.models.course import Course, CourseCompetency
from app.models.role import Role
from app.models.question import Question
from app.models.assessment import Assessment
from app.models.question import Answer
from app.models.learning import LearningContent, Progress, Recommendation
from app.security import hash_password

# Reuse the master data already maintained by seed.py.
from seed import ROLE_COMPETENCIES


# ============================================================
# DEMO EMPLOYEES
# ============================================================
# Department is currently a field on users.department; there is
# no separate departments table in the current schema.
DEMO_USERS = [
    {
        "email": "ananya.sharma@demo.gov.in",
        "full_name": "Ananya Sharma",
        "department": "National Statistical Office",
        "designation": "Statistical Officer",
        "role": "Statistical Officer",
        "education": "M.Sc. Statistics",
        "experience_years": 4,
    },
    {
        "email": "rahul.verma@demo.gov.in",
        "full_name": "Rahul Verma",
        "department": "National Statistical Office",
        "designation": "Data Analyst",
        "role": "Data Analyst",
        "education": "B.Tech Computer Science",
        "experience_years": 3,
    },
    {
        "email": "priya.nair@demo.gov.in",
        "full_name": "Priya Nair",
        "department": "National Sample Survey Office",
        "designation": "Senior Statistical Officer",
        "role": "Statistical Officer",
        "education": "M.A. Economics",
        "experience_years": 8,
    },
    {
        "email": "arjun.mehta@demo.gov.in",
        "full_name": "Arjun Mehta",
        "department": "State Directorate of Economics and Statistics",
        "designation": "Data Analyst",
        "role": "Data Analyst",
        "education": "M.Sc. Data Science",
        "experience_years": 2,
    },
    {
        "email": "sneha.rao@demo.gov.in",
        "full_name": "Sneha Rao",
        "department": "Ministry of Statistics and Programme Implementation",
        "designation": "Statistical Officer",
        "role": "Statistical Officer",
        "education": "M.Sc. Statistics",
        "experience_years": 5,
    },
    {
        "email": "vikram.singh@demo.gov.in",
        "full_name": "Vikram Singh",
        "department": "National Statistical Office",
        "designation": "Data Scientist",
        "role": "Data Scientist",
        "education": "M.Tech Artificial Intelligence",
        "experience_years": 4,
    },
    {
        "email": "kavya.iyer@demo.gov.in",
        "full_name": "Kavya Iyer",
        "department": "National Sample Survey Office",
        "designation": "Statistical Officer",
        "role": "Statistical Officer",
        "education": "M.Sc. Applied Statistics",
        "experience_years": 3,
    },
    {
        "email": "rohit.kumar@demo.gov.in",
        "full_name": "Rohit Kumar",
        "department": "State Directorate of Economics and Statistics",
        "designation": "System Admin",
        "role": "IT Officer",
        "access_role": "admin",
        "education": "B.Tech Computer Science",
        "experience_years": 5,
    },
    {
        "email": "neha.gupta@demo.gov.in",
        "full_name": "Neha Gupta",
        "department": "Ministry of Statistics and Programme Implementation",
        "designation": "Data Analyst",
        "role": "Data Analyst",
        "education": "MCA",
        "experience_years": 6,
    },
    {
        "email": "amit.joshi@demo.gov.in",
        "full_name": "Amit Joshi",
        "department": "National Statistical Office",
        "designation": "Senior Statistical Officer",
        "role": "Statistical Officer",
        "education": "M.A. Economics",
        "experience_years": 10,
    },
    {
        "email": "meera.patel@demo.gov.in",
        "full_name": "Meera Patel",
        "department": "Government Data and Digital Services Division",
        "designation": "IT Officer",
        "role": "IT Officer",
        "education": "B.Tech Information Technology",
        "experience_years": 5,
    },
    {
        "email": "dev.malhotra@demo.gov.in",
        "full_name": "Dev Malhotra",
        "department": "Government Data and Digital Services Division",
        "designation": "IT Officer",
        "role": "IT Officer",
        "education": "M.Tech Cybersecurity",
        "experience_years": 7,
    },
]


# Each profile intentionally has strengths and weaknesses so the
# dashboard/recommendation flow has something meaningful to display.
PROFILE_LEVELS = {
    "ananya.sharma@demo.gov.in": {
        "Python": 2, "SQL": 2, "Data Visualization": 2, "AI/ML": 1,
        "Survey Design": 4, "Sampling": 4, "Data Quality": 4,
        "Communication": 4, "Ethics": 4,
    },
    "rahul.verma@demo.gov.in": {
        "Python": 4, "SQL": 4, "Data Visualization": 4, "AI/ML": 2,
        "Statistical Analysis": 3, "Data Quality": 3,
        "Communication": 3, "APIs": 2,
    },
    "priya.nair@demo.gov.in": {
        "Survey Design": 5, "Sampling": 5, "Statistical Analysis": 5,
        "Data Quality": 4, "Metadata Standards": 4, "Python": 2,
        "SQL": 2, "Data Visualization": 2, "AI/ML": 1,
        "Communication": 5, "Ethics": 5,
    },
    "arjun.mehta@demo.gov.in": {
        "Python": 3, "SQL": 3, "Data Visualization": 3,
        "Statistical Analysis": 3, "Data Quality": 2, "APIs": 2,
        "Communication": 3,
    },
    "sneha.rao@demo.gov.in": {
        "Survey Design": 4, "Sampling": 3, "Statistical Analysis": 4,
        "Data Quality": 4, "Metadata Standards": 3, "Python": 2,
        "R": 2, "SQL": 2, "AI/ML": 1, "Data Visualization": 2,
        "Communication": 4, "Ethics": 4,
    },
    "vikram.singh@demo.gov.in": {
        "Python": 5, "AI/ML": 5, "SQL": 4, "Statistical Analysis": 5,
        "Data Visualization": 4, "Data Quality": 4, "Cloud Computing": 3,
        "APIs": 3, "Communication": 4,
    },
    "kavya.iyer@demo.gov.in": {
        "Survey Design": 3, "Sampling": 3, "Statistical Analysis": 3,
        "Data Quality": 3, "Metadata Standards": 2, "Python": 2,
        "R": 2, "SQL": 2, "Data Visualization": 2,
        "Communication": 3, "Ethics": 4,
    },
    "rohit.kumar@demo.gov.in": {
        "Survey Design": 2, "Sampling": 2, "Statistical Analysis": 2,
        "Data Quality": 2, "Metadata Standards": 1, "Python": 1,
        "SQL": 1, "Data Visualization": 1, "Communication": 2,
        "Ethics": 3,
    },
    "neha.gupta@demo.gov.in": {
        "Python": 4, "SQL": 5, "Data Visualization": 4, "R": 3,
        "Statistical Analysis": 4, "Data Quality": 4, "APIs": 3,
        "Open Data": 3, "Communication": 4, "Decision Making": 3,
    },
    "amit.joshi@demo.gov.in": {
        "Survey Design": 5, "Sampling": 5, "Statistical Analysis": 5,
        "Data Quality": 5, "Metadata Standards": 5, "National Accounts": 4,
        "Python": 2, "SQL": 2, "AI/ML": 1, "Data Visualization": 3,
        "Communication": 5, "Ethics": 5,
    },
    "meera.patel@demo.gov.in": {
        "APIs": 4, "Cloud Computing": 3, "Government Cloud": 3,
        "Cybersecurity": 4, "Data Privacy": 3, "Digital Signatures": 3,
        "Digital Public Infrastructure": 3, "SQL": 3, "Python": 2,
        "Communication": 3, "Project Management": 3,
    },
    "dev.malhotra@demo.gov.in": {
        "APIs": 5, "Cloud Computing": 4, "Government Cloud": 4,
        "Cybersecurity": 5, "Data Privacy": 5, "Digital Signatures": 4,
        "Digital Public Infrastructure": 4, "SQL": 4, "Python": 3,
        "Open Data": 4, "Communication": 4, "Project Management": 4,
    },
}


# ============================================================
# DEMO LEARNING CONTENT
# ============================================================
CONTENT = [
    ("Python for Data Analysis - Demo Material", "python_data_analysis_demo.pdf", "pdf"),
    ("Survey Sampling Techniques - Demo Material", "survey_sampling_demo.pdf", "pdf"),
    ("Data Quality and Metadata - Demo Material", "data_quality_metadata_demo.pdf", "pdf"),
    ("Machine Learning Fundamentals - Demo Material", "machine_learning_demo.pptx", "pptx"),
    ("Cybersecurity and Data Privacy - Demo Material", "cybersecurity_privacy_demo.pdf", "pdf"),
]


def get_or_create_user(db, data, role_map):
    user = db.scalar(select(User).where(User.email == data["email"]))

    access_role = data.get("access_role", "employee")
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=data["email"],
            password_hash=hash_password("Demo@12345"),
            full_name=data["full_name"],
            access_role=access_role,
            designation=data["designation"],
            department=data["department"],
            job_role_id=role_map[data["role"]].id,
            education=data["education"],
            experience_years=data["experience_years"],
            is_active=True,
        )
        db.add(user)
        db.flush()
    else:
        user.full_name = data["full_name"]
        user.access_role = access_role
        user.designation = data["designation"]
        user.department = data["department"]
        user.job_role_id = role_map[data["role"]].id
        user.education = data["education"]
        user.experience_years = data["experience_years"]
        user.is_active = True

    return user


def seed_demo():
    db = SessionLocal()

    try:
        print("Starting demo-data seed...")
        print()

        # --------------------------------------------------------
        # 1. LOAD EXISTING MASTER DATA
        # --------------------------------------------------------
        roles = db.scalars(select(Role)).all()
        role_map = {r.name: r for r in roles}

        competencies = db.scalars(
            select(Competency).where(Competency.is_active.is_(True))
        ).all()
        competency_map = {c.name: c for c in competencies}

        courses = db.scalars(
            select(Course).where(Course.is_active.is_(True))
        ).all()
        course_map = {c.title: c for c in courses}

        questions = db.scalars(
            select(Question).where(Question.is_active.is_(True))
        ).all()
        questions_by_competency = {}
        for q in questions:
            questions_by_competency.setdefault(q.competency_id, []).append(q)

        print(f"Existing roles: {len(role_map)}")
        print(f"Existing competencies: {len(competency_map)}")
        print(f"Existing courses: {len(course_map)}")
        print(f"Existing questions: {len(questions)}")

        # --------------------------------------------------------
        # 2. EMPLOYEES
        # --------------------------------------------------------
        user_map = {}

        for data in DEMO_USERS:
            user = get_or_create_user(db, data, role_map)
            user_map[user.email] = user

        print(f"Demo employees ready: {len(user_map)}")

        # --------------------------------------------------------
        # 3. USER COMPETENCY PROFILES
        # --------------------------------------------------------
        competency_count = 0
        assessed_at = datetime.now(timezone.utc) - timedelta(days=7)

        for data in DEMO_USERS:
            user = user_map[data["email"]]
            role_mappings = ROLE_COMPETENCIES[data["role"]]
            profile = PROFILE_LEVELS[data["email"]]

            for competency_name, (required_level, _critical) in role_mappings.items():
                competency = competency_map.get(competency_name)
                if competency is None:
                    continue

                current_level = profile.get(
                    competency_name,
                    max(1, required_level - 1),
                )

                existing = db.scalar(
                    select(UserCompetency).where(
                        UserCompetency.user_id == user.id,
                        UserCompetency.competency_id == competency.id,
                    )
                )

                if existing is None:
                    existing = UserCompetency(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        competency_id=competency.id,
                        current_level=current_level,
                        source="assessment",
                        last_assessed_at=assessed_at,
                    )
                    db.add(existing)
                else:
                    existing.current_level = current_level
                    existing.source = "assessment"
                    existing.last_assessed_at = assessed_at

                competency_count += 1

        print(f"User competency records ready: {competency_count}")

        # --------------------------------------------------------
        # 4. LEARNING CONTENT
        # --------------------------------------------------------
        content_map = {}

        for title, file_name, file_type in CONTENT:
            content = db.scalar(
                select(LearningContent).where(
                    LearningContent.file_name == file_name
                )
            )

            if content is None:
                content = LearningContent(
                    id=uuid.uuid4(),
                    title=title,
                    file_name=file_name,
                    file_type=file_type,
                    storage_path=f"demo/{file_name}",
                    source="demo",
                    status="ready",
                )
                db.add(content)
                db.flush()
            else:
                content.title = title
                content.file_type = file_type
                content.storage_path = f"demo/{file_name}"
                content.source = "demo"
                content.status = "ready"

            content_map[title] = content

        print(f"Learning content ready: {len(content_map)}")

        # Attach representative existing questions to demo learning content.
        content_competencies = {
            "Python for Data Analysis - Demo Material": "Python",
            "Survey Sampling Techniques - Demo Material": "Sampling",
            "Data Quality and Metadata - Demo Material": "Data Quality",
            "Machine Learning Fundamentals - Demo Material": "AI/ML",
            "Cybersecurity and Data Privacy - Demo Material": "Cybersecurity",
        }

        for content_title, competency_name in content_competencies.items():
            content = content_map[content_title]
            competency = competency_map.get(competency_name)
            if not competency:
                continue

            for question in questions_by_competency.get(competency.id, [])[:3]:
                question.source_content_id = content.id

        # --------------------------------------------------------
        # 5. INITIAL ASSESSMENTS + ANSWERS
        # --------------------------------------------------------
        assessment_count = 0
        answer_count = 0

        for index, data in enumerate(DEMO_USERS):
            user = user_map[data["email"]]

            existing_assessment = db.scalar(
                select(Assessment).where(
                    Assessment.user_id == user.id,
                    Assessment.assessment_type == "initial",
                )
            )

            if existing_assessment is not None:
                assessment = existing_assessment
            else:
                assessment = Assessment(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    assessment_type="initial",
                    status="completed",
                    score=Decimal(str(72 + (index % 5) * 5)),
                    started_at=datetime.now(timezone.utc) - timedelta(days=8),
                    completed_at=datetime.now(timezone.utc) - timedelta(days=7),
                )
                db.add(assessment)
                db.flush()
                assessment_count += 1

            # Add a few answers if this assessment has none.
            existing_answer_count = db.scalar(
                select(func.count(Answer.id)).where(
                    Answer.assessment_id == assessment.id
                )
            )

            if existing_answer_count == 0:
                role = data["role"]
                role_comp_names = list(ROLE_COMPETENCIES[role].keys())[:5]

                for comp_name in role_comp_names:
                    competency = competency_map.get(comp_name)
                    if not competency:
                        continue

                    q_list = questions_by_competency.get(competency.id, [])
                    if not q_list:
                        continue

                    question = q_list[0]
                    # Most demo answers are correct; every third employee
                    # intentionally has one incorrect answer.
                    is_correct = not (
                        index % 3 == 2 and comp_name == role_comp_names[0]
                    )

                    answer = Answer(
                        id=uuid.uuid4(),
                        assessment_id=assessment.id,
                        question_id=question.id,
                        selected_answer=question.correct_answer if is_correct else "B",
                        is_correct=is_correct,
                        score=1.0 if is_correct else 0.0,
                    )
                    db.add(answer)
                    answer_count += 1

        print(f"Initial assessments created: {assessment_count}")
        print(f"Assessment answers created: {answer_count}")

        # --------------------------------------------------------
        # 6. SKILL-GAP REPRESENTATION + RECOMMENDATIONS
        # --------------------------------------------------------
        recommendation_count = 0

        for data in DEMO_USERS:
            user = user_map[data["email"]]
            role = role_map[data["role"]]
            profile = PROFILE_LEVELS[data["email"]]

            role_rows = db.scalars(
                select(RoleCompetency).where(
                    RoleCompetency.role_id == role.id
                )
            ).all()

            candidates = []

            for row in role_rows:
                competency = competency_map.get(
                    next(
                        (
                            name
                            for name, comp in competency_map.items()
                            if comp.id == row.competency_id
                        ),
                        "",
                    )
                )
                if competency is None:
                    continue

                current = profile.get(
                    competency.name,
                    max(1, row.required_level - 1),
                )
                gap = max(row.required_level - current, 0)

                if gap > 0:
                    priority = min(
                        100,
                        gap * 20 + (20 if row.is_critical else 0),
                    )
                    candidates.append(
                        (priority, gap, row.is_critical, competency)
                    )

            candidates.sort(key=lambda x: (-x[0], -x[1]))

            # Keep the dashboard focused: top 3 gaps per employee.
            for priority, gap, is_critical, competency in candidates[:3]:
                course = None

                # Prefer a course explicitly mapped to this competency.
                course_rows = db.scalars(
                    select(Course)
                    .join(CourseCompetency, CourseCompetency.course_id == Course.id)
                    .where(CourseCompetency.competency_id == competency.id)
                    .where(Course.is_active.is_(True))
                    .order_by(Course.title)
                ).all()

                if course_rows:
                    course = course_rows[0]

                if course is None:
                    continue

                existing = db.scalar(
                    select(Recommendation).where(
                        Recommendation.user_id == user.id,
                        Recommendation.course_id == course.id,
                        Recommendation.competency_id == competency.id,
                    )
                )

                if existing is None:
                    recommendation = Recommendation(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        course_id=course.id,
                        competency_id=competency.id,
                        gap_score=Decimal(str(gap)),
                        priority_score=Decimal(str(priority)),
                        reason=(
                            f"Your current {competency.name} level is "
                            f"below the requirement for your {data['role']} role. "
                            f"This course is recommended to close the identified "
                            f"{'critical ' if is_critical else ''}skill gap."
                        ),
                        status="pending",
                    )
                    db.add(recommendation)
                    recommendation_count += 1

        print(f"Recommendations created: {recommendation_count}")

        # --------------------------------------------------------
        # 7. LEARNING PROGRESS
        # --------------------------------------------------------
        progress_count = 0

        all_courses = list(course_map.values())

        for index, data in enumerate(DEMO_USERS):
            user = user_map[data["email"]]

            # Give each employee a different learning state.
            if not all_courses:
                continue

            selected_courses = all_courses[index % len(all_courses):]
            selected_courses = selected_courses[:2]

            for course_index, course in enumerate(selected_courses):
                existing = db.scalar(
                    select(Progress).where(
                        Progress.user_id == user.id,
                        Progress.course_id == course.id,
                    )
                )

                if existing is not None:
                    continue

                if course_index == 0:
                    percent = [100, 75, 50, 25, 90][index % 5]
                    status = "completed" if percent == 100 else "in_progress"
                    started = datetime.now(timezone.utc) - timedelta(days=20)
                    completed = (
                        datetime.now(timezone.utc) - timedelta(days=3)
                        if percent == 100
                        else None
                    )
                else:
                    percent = 0
                    status = "not_started"
                    started = None
                    completed = None

                db.add(
                    Progress(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        course_id=course.id,
                        status=status,
                        progress_percentage=percent,
                        started_at=started,
                        completed_at=completed,
                    )
                )
                progress_count += 1

        print(f"Learning progress records created: {progress_count}")

        db.commit()

        print()
        print("=" * 50)
        print("DEMO DATA SEED COMPLETED")
        print("=" * 50)
        print(f"Employees:              {len(user_map)}")
        print(f"Competency profiles:    {competency_count}")
        print(f"Learning content:       {len(content_map)}")
        print(f"Assessments:            {assessment_count}")
        print(f"Answers:                {answer_count}")
        print(f"Recommendations:        {recommendation_count}")
        print(f"Progress records:       {progress_count}")
        print()
        print("Demo login password for all demo employees: Demo@12345")
        print("=" * 50)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()