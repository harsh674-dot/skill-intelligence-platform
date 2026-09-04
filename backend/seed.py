import uuid

from sqlalchemy import select

from app.database import SessionLocal
from app.models.role import Role
from app.models.competency import (
    Competency,
    RoleCompetency,
)
from app.models.course import (
    Course,
    CourseCompetency,
)
from app.models.question import Question


# ============================================================
# ROLES
# ============================================================

ROLES = [
    {
        "name": "Statistical Officer",
        "description": (
            "Officer responsible for statistical analysis, "
            "survey data and official statistics."
        ),
    },
    {
        "name": "Data Analyst",
        "description": (
            "Professional responsible for data analysis, "
            "visualization and reporting."
        ),
    },
    {
        "name": "Data Scientist",
        "description": (
            "Professional working with statistical modelling, "
            "machine learning and data science."
        ),
    },
    {
        "name": "IT Officer",
        "description": (
            "Officer responsible for IT systems, APIs, "
            "cloud infrastructure and cybersecurity."
        ),
    },
]


# ============================================================
# COMPETENCIES
# ============================================================

COMPETENCIES = [
    {
        "name": "Sampling",
        "domain": "Statistical",
        "description": (
            "Knowledge of sampling techniques used "
            "in statistical surveys."
        ),
    },
    {
        "name": "Survey Design",
        "domain": "Statistical",
        "description": (
            "Ability to design statistically sound "
            "surveys and questionnaires."
        ),
    },
    {
        "name": "Statistical Analysis",
        "domain": "Statistical",
        "description": (
            "Ability to apply statistical methods "
            "to analyse datasets."
        ),
    },
    {
        "name": "Data Quality",
        "domain": "Statistical",
        "description": (
            "Ability to assess and improve the "
            "quality of statistical data."
        ),
    },
    {
        "name": "Python",
        "domain": "Technical",
        "description": (
            "Programming and data analysis using Python."
        ),
    },
    {
        "name": "SQL",
        "domain": "Technical",
        "description": (
            "Ability to query, manipulate and analyse "
            "relational data."
        ),
    },
    {
        "name": "Data Visualization",
        "domain": "Technical",
        "description": (
            "Ability to communicate insights through "
            "charts and dashboards."
        ),
    },
    {
        "name": "Machine Learning",
        "domain": "Technical",
        "description": (
            "Knowledge of machine learning algorithms "
            "and workflows."
        ),
    },
    {
        "name": "GIS",
        "domain": "Technical",
        "description": (
            "Use of geographic information systems "
            "for spatial analysis."
        ),
    },
    {
        "name": "Cybersecurity",
        "domain": "Digital Governance",
        "description": (
            "Understanding of cybersecurity principles "
            "and secure systems."
        ),
    },
    {
        "name": "Data Privacy",
        "domain": "Digital Governance",
        "description": (
            "Understanding of data protection "
            "and privacy principles."
        ),
    },
    {
        "name": "Communication",
        "domain": "Behavioural",
        "description": (
            "Ability to communicate analytical "
            "findings clearly."
        ),
    },
]


# ============================================================
# ROLE → COMPETENCY
#
# Format:
# "Competency": (required_level, is_critical)
#
# Levels:
# 1 = Beginner
# 2 = Basic
# 3 = Intermediate
# 4 = Advanced
# 5 = Expert
# ============================================================

ROLE_COMPETENCIES = {
    "Statistical Officer": {
        "Sampling": (4, True),
        "Survey Design": (4, True),
        "Statistical Analysis": (4, True),
        "Data Quality": (4, True),
        "Python": (3, False),
        "SQL": (3, False),
        "Data Visualization": (3, False),
        "Communication": (4, True),
    },

    "Data Analyst": {
        "Statistical Analysis": (4, True),
        "Python": (4, True),
        "SQL": (4, True),
        "Data Visualization": (4, True),
        "Data Quality": (3, False),
        "Communication": (4, True),
    },

    "Data Scientist": {
        "Statistical Analysis": (4, True),
        "Python": (5, True),
        "SQL": (4, False),
        "Machine Learning": (5, True),
        "Data Visualization": (3, False),
        "Data Quality": (4, True),
    },

    "IT Officer": {
        "SQL": (3, False),
        "Python": (3, False),
        "Cybersecurity": (5, True),
        "Data Privacy": (4, True),
        "Communication": (3, False),
    },
}


# ============================================================
# COURSES
# ============================================================

COURSES = [
    {
        "title": "Python for Data Analysis",
        "description": (
            "Learn Python fundamentals and data analysis "
            "using Pandas and NumPy."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "PYTHON-001",
        "url": "https://example.com/python-data-analysis",
        "duration_minutes": 240,
        "level": "beginner",
        "competencies": {
            "Python": 3,
        },
    },

    {
        "title": "Advanced Python for Data Science",
        "description": (
            "Advanced Python programming for data science "
            "and analytical workflows."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "PYTHON-002",
        "url": "https://example.com/advanced-python",
        "duration_minutes": 360,
        "level": "advanced",
        "competencies": {
            "Python": 5,
            "Data Visualization": 3,
        },
    },

    {
        "title": "SQL Fundamentals",
        "description": (
            "Learn relational databases, SQL queries "
            "and data manipulation."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "SQL-001",
        "url": "https://example.com/sql-fundamentals",
        "duration_minutes": 180,
        "level": "beginner",
        "competencies": {
            "SQL": 3,
        },
    },

    {
        "title": "Advanced SQL and Analytics",
        "description": (
            "Advanced SQL queries, joins, aggregation "
            "and analytical techniques."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "SQL-002",
        "url": "https://example.com/advanced-sql",
        "duration_minutes": 300,
        "level": "advanced",
        "competencies": {
            "SQL": 5,
            "Data Quality": 4,
        },
    },

    {
        "title": "Statistical Methods for Official Statistics",
        "description": (
            "Core statistical methods used in official "
            "statistical systems."
        ),
        "provider": "NSSTA Mock Catalogue",
        "source": "mock",
        "external_id": "STAT-001",
        "url": "https://example.com/statistical-methods",
        "duration_minutes": 360,
        "level": "intermediate",
        "competencies": {
            "Statistical Analysis": 4,
            "Data Quality": 4,
        },
    },

    {
        "title": "Survey Sampling Techniques",
        "description": (
            "Sampling methodologies for official "
            "statistical surveys."
        ),
        "provider": "NSSTA Mock Catalogue",
        "source": "mock",
        "external_id": "STAT-002",
        "url": "https://example.com/sampling",
        "duration_minutes": 300,
        "level": "advanced",
        "competencies": {
            "Sampling": 4,
            "Survey Design": 4,
        },
    },

    {
        "title": "Survey Design Fundamentals",
        "description": (
            "Principles of questionnaire and survey design."
        ),
        "provider": "NSSTA Mock Catalogue",
        "source": "mock",
        "external_id": "STAT-003",
        "url": "https://example.com/survey-design",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {
            "Survey Design": 4,
        },
    },

    {
        "title": "Data Visualization and Storytelling",
        "description": (
            "Create effective visualizations and communicate "
            "analytical insights."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "VIZ-001",
        "url": "https://example.com/data-visualization",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {
            "Data Visualization": 4,
            "Communication": 4,
        },
    },

    {
        "title": "Machine Learning Fundamentals",
        "description": (
            "Introduction to supervised and unsupervised "
            "machine learning."
        ),
        "provider": "Internal Training",
        "source": "mock",
        "external_id": "ML-001",
        "url": "https://example.com/ml-fundamentals",
        "duration_minutes": 360,
        "level": "intermediate",
        "competencies": {
            "Machine Learning": 3,
            "Python": 3,
        },
    },

    {
        "title": "Cybersecurity for Government Systems",
        "description": (
            "Cybersecurity fundamentals for government "
            "digital systems."
        ),
        "provider": "Government Training",
        "source": "mock",
        "external_id": "SEC-001",
        "url": "https://example.com/cybersecurity",
        "duration_minutes": 240,
        "level": "intermediate",
        "competencies": {
            "Cybersecurity": 4,
            "Data Privacy": 4,
        },
    },
]


# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "competency": "Sampling",
        "question_text": (
            "Which sampling method gives every member of "
            "a population an equal probability of selection?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "Simple random sampling",
            "B": "Convenience sampling",
            "C": "Snowball sampling",
            "D": "Judgment sampling",
        },
        "correct_answer": "A",
        "explanation": (
            "Simple random sampling gives every population "
            "member an equal probability of selection."
        ),
    },

    {
        "competency": "Statistical Analysis",
        "question_text": (
            "Which measure represents the middle value "
            "of an ordered dataset?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "Mean",
            "B": "Median",
            "C": "Variance",
            "D": "Range",
        },
        "correct_answer": "B",
        "explanation": (
            "The median is the middle value when "
            "observations are ordered."
        ),
    },

    {
        "competency": "Python",
        "question_text": (
            "Which Python library is commonly used "
            "for tabular data analysis?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "Pandas",
            "B": "Flask",
            "C": "Requests",
            "D": "Tkinter",
        },
        "correct_answer": "A",
        "explanation": (
            "Pandas provides DataFrame and Series structures "
            "for tabular data analysis."
        ),
    },

    {
        "competency": "SQL",
        "question_text": (
            "Which SQL statement is used to retrieve "
            "data from a table?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "INSERT",
            "B": "UPDATE",
            "C": "SELECT",
            "D": "DELETE",
        },
        "correct_answer": "C",
        "explanation": (
            "SELECT is used to retrieve rows from "
            "one or more tables."
        ),
    },

    {
        "competency": "Data Visualization",
        "question_text": (
            "Which chart is generally appropriate for "
            "showing the distribution of a continuous variable?"
        ),
        "question_type": "mcq",
        "difficulty": "intermediate",
        "options": {
            "A": "Histogram",
            "B": "Pie chart",
            "C": "Radar chart",
            "D": "Tree map",
        },
        "correct_answer": "A",
        "explanation": (
            "Histograms show the frequency distribution "
            "of continuous numerical data."
        ),
    },

    {
        "competency": "Machine Learning",
        "question_text": (
            "Which type of machine learning uses "
            "labelled training data?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "Supervised learning",
            "B": "Unsupervised learning",
            "C": "Reinforcement learning",
            "D": "Clustering",
        },
        "correct_answer": "A",
        "explanation": (
            "Supervised learning trains models using "
            "labelled input-output examples."
        ),
    },

    {
        "competency": "Cybersecurity",
        "question_text": (
            "Which practice provides an additional "
            "security layer beyond a password?"
        ),
        "question_type": "mcq",
        "difficulty": "beginner",
        "options": {
            "A": "Multi-factor authentication",
            "B": "Disabling encryption",
            "C": "Sharing passwords",
            "D": "Using public Wi-Fi",
        },
        "correct_answer": "A",
        "explanation": (
            "Multi-factor authentication requires "
            "an additional authentication factor."
        ),
    },

    {
        "competency": "Data Privacy",
        "question_text": (
            "Which principle means that personal data "
            "should only be collected for specified purposes?"
        ),
        "question_type": "mcq",
        "difficulty": "intermediate",
        "options": {
            "A": "Purpose limitation",
            "B": "Data duplication",
            "C": "Unlimited retention",
            "D": "Open access",
        },
        "correct_answer": "A",
        "explanation": (
            "Purpose limitation restricts collection and "
            "processing to specified legitimate purposes."
        ),
    },
]


# ============================================================
# SEED DATABASE
# ============================================================

def seed_database():
    db = SessionLocal()

    try:
        print("Starting database seed...")
        print()

        # ====================================================
        # 1. ROLES
        # ====================================================

        role_map = {}

        for role_data in ROLES:

            role = db.scalar(
                select(Role).where(
                    Role.name == role_data["name"]
                )
            )

            if role is None:
                role = Role(
                    id=uuid.uuid4(),
                    name=role_data["name"],
                    description=role_data["description"],
                    is_active=True,
                )

                db.add(role)
                db.flush()

            role_map[role.name] = role

        print(f"Roles ready: {len(role_map)}")

        # ====================================================
        # 2. COMPETENCIES
        # ====================================================

        competency_map = {}

        for competency_data in COMPETENCIES:

            competency = db.scalar(
                select(Competency).where(
                    Competency.name
                    == competency_data["name"]
                )
            )

            if competency is None:
                competency = Competency(
                    id=uuid.uuid4(),
                    name=competency_data["name"],
                    domain=competency_data["domain"],
                    description=competency_data["description"],
                    is_active=True,
                )

                db.add(competency)
                db.flush()

            competency_map[
                competency.name
            ] = competency

        print(
            f"Competencies ready: "
            f"{len(competency_map)}"
        )

        # ====================================================
        # 3. ROLE → COMPETENCY
        # ====================================================

        role_mapping_count = 0

        for role_name, mappings in ROLE_COMPETENCIES.items():

            role = role_map[role_name]

            for competency_name, values in mappings.items():

                required_level, is_critical = values

                competency = competency_map[
                    competency_name
                ]

                existing = db.scalar(
                    select(RoleCompetency).where(
                        RoleCompetency.role_id == role.id,
                        RoleCompetency.competency_id
                        == competency.id,
                    )
                )

                if existing is None:

                    mapping = RoleCompetency(
                        id=uuid.uuid4(),
                        role_id=role.id,
                        competency_id=competency.id,
                        required_level=required_level,
                        is_critical=is_critical,
                    )

                    db.add(mapping)

                role_mapping_count += 1

        print(
            f"Role-competency mappings: "
            f"{role_mapping_count}"
        )

        # ====================================================
        # 4. COURSES
        # ====================================================

        course_map = {}

        for course_data in COURSES:

            course = db.scalar(
                select(Course).where(
                    Course.external_id
                    == course_data["external_id"]
                )
            )

            if course is None:

                course = Course(
                    id=uuid.uuid4(),
                    title=course_data["title"],
                    description=course_data["description"],
                    provider=course_data["provider"],
                    source=course_data["source"],
                    external_id=course_data["external_id"],
                    url=course_data["url"],
                    duration_minutes=course_data[
                        "duration_minutes"
                    ],
                    level=course_data["level"],
                    is_active=True,
                )

                db.add(course)
                db.flush()

            course_map[
                course.external_id
            ] = course

        print(
            f"Courses ready: "
            f"{len(course_map)}"
        )

        # ====================================================
        # 5. COURSE → COMPETENCY
        # ====================================================

        course_mapping_count = 0

        for course_data in COURSES:

            course = course_map[
                course_data["external_id"]
            ]

            for competency_name, target_level in (
                course_data["competencies"].items()
            ):

                competency = competency_map[
                    competency_name
                ]

                existing = db.scalar(
                    select(CourseCompetency).where(
                        CourseCompetency.course_id
                        == course.id,
                        CourseCompetency.competency_id
                        == competency.id,
                    )
                )

                if existing is None:

                    mapping = CourseCompetency(
                        id=uuid.uuid4(),
                        course_id=course.id,
                        competency_id=competency.id,
                        target_level=target_level,
                    )

                    db.add(mapping)

                course_mapping_count += 1

        print(
            f"Course-competency mappings: "
            f"{course_mapping_count}"
        )

        # ====================================================
        # 6. QUESTIONS
        # ====================================================

        question_count = 0

        for question_data in QUESTIONS:

            competency = competency_map[
                question_data["competency"]
            ]

            existing = db.scalar(
                select(Question).where(
                    Question.question_text
                    == question_data["question_text"]
                )
            )

            if existing is not None:
                continue

            question = Question(
                id=uuid.uuid4(),
                competency_id=competency.id,
                question_text=question_data["question_text"],
                question_type=question_data["question_type"],
                difficulty=question_data["difficulty"],
                options=question_data["options"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                is_active=True,
            )

            db.add(question)

            question_count += 1

        print(
            f"Questions added: "
            f"{question_count}"
        )

        # ====================================================
        # COMMIT
        # ====================================================

        db.commit()

        print()
        print("========================================")
        print("DATABASE SEED COMPLETED")
        print("========================================")
        print(f"Roles:                  {len(role_map)}")
        print(
            f"Competencies:           "
            f"{len(competency_map)}"
        )
        print(
            f"Role mappings:          "
            f"{role_mapping_count}"
        )
        print(
            f"Courses:                "
            f"{len(course_map)}"
        )
        print(
            f"Course mappings:        "
            f"{course_mapping_count}"
        )
        print(
            f"Questions added:        "
            f"{question_count}"
        )
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()