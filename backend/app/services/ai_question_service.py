import uuid

from sqlalchemy.orm import Session

from app.models.content_chunk import ContentChunk
from app.models.ai_question import AIGeneratedQuestion
from app.models.learning import LearningContent
from app.services.question_generator import generate_mcq


def generate_questions_for_content(
    db: Session,
    content_id: uuid.UUID,
    count: int = 5,
    difficulty: str = "beginner",
) -> list[AIGeneratedQuestion]:
    """
    Generate MCQs from uploaded learning content
    and save them to the database.
    """

    # ---------------------------------------------------------
    # 1. Validate count
    # ---------------------------------------------------------

    if count < 1:
        raise ValueError("count must be at least 1.")

    if count > 20:
        raise ValueError("count cannot be greater than 20.")

    # ---------------------------------------------------------
    # 2. Find learning content
    # ---------------------------------------------------------

    learning_content = (
        db.query(LearningContent)
        .filter(
            LearningContent.id == content_id
        )
        .first()
    )

    if not learning_content:
        raise ValueError(
            "Learning content not found."
        )

    # ---------------------------------------------------------
    # 3. Get content chunks
    # ---------------------------------------------------------

    chunks = (
        db.query(ContentChunk)
        .filter(
            ContentChunk.learning_content_id
            == content_id
        )
        .order_by(
            ContentChunk.chunk_index
        )
        .all()
    )

    if not chunks:
        raise ValueError(
            "No content chunks found for this learning content."
        )

    # ---------------------------------------------------------
    # 4. Combine chunks
    # ---------------------------------------------------------

    context_parts = []

    for chunk in chunks:
        if chunk.chunk_text:
            context_parts.append(
                chunk.chunk_text.strip()
            )

    context = "\n\n".join(
        context_parts
    )

    if not context.strip():
        raise ValueError(
            "Learning content contains no usable text."
        )

    # ---------------------------------------------------------
    # 5. Generate questions
    # ---------------------------------------------------------

    generated_questions = []

    for _ in range(count):

        try:

            question_data = generate_mcq(
                context=context,
                difficulty=difficulty,
            )

        except Exception as exc:

            print(
                f"Question generation failed: {exc}"
            )

            continue

        # -----------------------------------------------------
        # 6. Create database object
        # -----------------------------------------------------

        question = AIGeneratedQuestion(
            id=uuid.uuid4(),
            learning_content_id=content_id,
            competency_id=None,
            question_text=question_data[
                "question_text"
            ],
            question_type="mcq",
            difficulty=difficulty,
            options=question_data[
                "options"
            ],
            correct_answer=question_data[
                "correct_answer"
            ],
            explanation=question_data.get(
                "explanation"
            ),
            source_chunk_ids=[
                str(chunk.id)
                for chunk in chunks
            ],
            generation_model="google/flan-t5-base",
            status="pending",
        )

        db.add(question)

        generated_questions.append(
            question
        )

    # ---------------------------------------------------------
    # 7. Make sure at least one question was generated
    # ---------------------------------------------------------

    if not generated_questions:
        db.rollback()

        raise ValueError(
            "Could not generate any valid questions."
        )

    # ---------------------------------------------------------
    # 8. Save to database
    # ---------------------------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise

    # ---------------------------------------------------------
    # 9. Refresh objects
    # ---------------------------------------------------------

    for question in generated_questions:
        db.refresh(question)

    return generated_questions