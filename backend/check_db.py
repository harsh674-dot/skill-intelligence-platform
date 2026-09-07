from app.database import SessionLocal
from sqlalchemy import text

tables = [
    "users",
    "roles",
    "competencies",
    "role_competencies",
    "courses",
    "course_competencies",
    "questions",
    "assessments",
    "answers",
    "learning_content",
    "progress",
    "recommendations",
    "user_competencies",
]

db = SessionLocal()

try:
    for table in tables:
        count = db.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()

        print(f"{table}: {count}")
finally:
    db.close()
