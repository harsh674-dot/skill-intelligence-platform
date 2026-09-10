from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.learning import LearningContent
from app.models.content_chunk import ContentChunk
from app.models.user import User
from app.services.document_parser import extract_text
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embedding
from app.services.question_generator import generate_mcq


router = APIRouter(
    prefix="/learning",
    tags=["Learning"],
)


# =========================================================
# FILE STORAGE
# =========================================================

UPLOAD_DIR = Path("uploads/learning")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


# =========================================================
# UPLOAD LEARNING CONTENT
# =========================================================

@router.post("/upload")
async def upload_learning_content(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Upload learning material and process it through:

    1. File validation
    2. File storage
    3. Text extraction
    4. Text chunking
    5. Local embedding generation
    6. PostgreSQL/pgvector storage
    """

    # -----------------------------------------------------
    # 1. Validate file type
    # -----------------------------------------------------

    file_type = ALLOWED_TYPES.get(file.content_type)

    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. "
                "Only PDF, DOCX and TXT files are supported."
            ),
        )

    # -----------------------------------------------------
    # 2. Validate filename
    # -----------------------------------------------------

    safe_name = Path(
        file.filename or "uploaded_file"
    ).name

    if not safe_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name.",
        )

    # -----------------------------------------------------
    # 3. Generate content ID
    # -----------------------------------------------------

    content_id = uuid.uuid4()

    storage_path = (
        UPLOAD_DIR
        / f"{content_id}_{safe_name}"
    )

    # -----------------------------------------------------
    # 4. Read uploaded file
    # -----------------------------------------------------

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {exc}",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # -----------------------------------------------------
    # 5. Save uploaded file
    # -----------------------------------------------------

    try:
        storage_path.write_bytes(file_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save uploaded file: {exc}",
        )

    # -----------------------------------------------------
    # 6. Extract text
    # -----------------------------------------------------

    try:
        extracted_text = extract_text(
            str(storage_path),
            file_type,
        )

    except Exception as exc:

        storage_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not extract document text: {exc}",
        )

    # -----------------------------------------------------
    # 7. Validate extracted text
    # -----------------------------------------------------

    if not extracted_text or not extracted_text.strip():

        storage_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The uploaded document contains "
                "no extractable text."
            ),
        )

    # -----------------------------------------------------
    # 8. Split text into chunks
    # -----------------------------------------------------

    try:

        chunks = chunk_text(
            extracted_text
        )

    except Exception as exc:

        storage_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not chunk document text: {exc}",
        )

    if not chunks:

        storage_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The document could not be divided "
                "into content chunks."
            ),
        )

    # -----------------------------------------------------
    # 9. Create LearningContent
    # -----------------------------------------------------

    learning_content = LearningContent(
        id=content_id,
        title=safe_name,
        file_name=safe_name,
        file_type=file_type,
        storage_path=str(storage_path),
        source="admin_upload",
        uploaded_by=current_user.id,
        status="processing",
    )

    db.add(learning_content)

    # -----------------------------------------------------
    # 10. Generate embeddings
    # -----------------------------------------------------

    content_chunks = []

    try:

        for index, chunk in enumerate(chunks):

            if not chunk or not chunk.strip():
                continue

            embedding = generate_embedding(
                chunk
            )

            # Safety check
            if len(embedding) != 384:
                raise ValueError(
                    "Embedding dimension mismatch. "
                    f"Expected 384, got {len(embedding)}."
                )

            content_chunk = ContentChunk(
                id=uuid.uuid4(),
                learning_content_id=content_id,
                chunk_index=index,
                chunk_text=chunk,
                embedding=embedding,
            )

            db.add(content_chunk)

            content_chunks.append(
                content_chunk
            )

    except Exception as exc:

        db.rollback()

        storage_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Could not generate embeddings "
                f"for the uploaded content: {exc}"
            ),
        )

    # -----------------------------------------------------
    # 11. Validate chunks
    # -----------------------------------------------------

    if not content_chunks:

        db.rollback()

        storage_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid content chunks were generated.",
        )

    # -----------------------------------------------------
    # 12. Mark content as ready
    # -----------------------------------------------------

    learning_content.status = "ready"

    # -----------------------------------------------------
    # 13. Commit transaction
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(
            learning_content
        )

    except Exception as exc:

        db.rollback()

        storage_path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to save learning content "
                f"to the database: {exc}"
            ),
        )

    # -----------------------------------------------------
    # 14. Return result
    # -----------------------------------------------------

    return {
        "id": str(
            learning_content.id
        ),
        "file_name": (
            learning_content.file_name
        ),
        "file_type": (
            learning_content.file_type
        ),
        "status": (
            learning_content.status
        ),
        "text_length": len(
            extracted_text
        ),
        "chunk_count": len(
            content_chunks
        ),
        "embeddings_generated": len(
            content_chunks
        ),
        "embedding_dimensions": 384,
    }


# =========================================================
# GENERATE MCQ FROM UPLOADED CONTENT
# =========================================================

@router.post("/{content_id}/generate-mcq")
def generate_mcq_from_content(
    content_id: uuid.UUID,
    difficulty: str = "beginner",
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Generate an MCQ from the uploaded learning content.

    The content chunks are retrieved from PostgreSQL,
    combined into context, and passed to the local
    question-generation model.
    """

    # -----------------------------------------------------
    # 1. Validate difficulty
    # -----------------------------------------------------

    allowed_difficulties = {
        "beginner",
        "intermediate",
        "advanced",
    }

    if difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid difficulty. "
                "Use beginner, intermediate or advanced."
            ),
        )

    # -----------------------------------------------------
    # 2. Find learning content
    # -----------------------------------------------------

    learning_content = (
        db.query(LearningContent)
        .filter(
            LearningContent.id == content_id
        )
        .first()
    )

    if not learning_content:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning content not found.",
        )

    # -----------------------------------------------------
    # 3. Check content status
    # -----------------------------------------------------

    if learning_content.status != "ready":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Learning content is not ready "
                "for question generation."
            ),
        )

    # -----------------------------------------------------
    # 4. Retrieve chunks
    # -----------------------------------------------------

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

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No content chunks found "
                "for this learning material."
            ),
        )

    # -----------------------------------------------------
    # 5. Build context
    # -----------------------------------------------------

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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The learning content contains "
                "no usable text."
            ),
        )

    # -----------------------------------------------------
    # 6. Generate MCQ
    # -----------------------------------------------------

    try:

        generated_question = generate_mcq(
            context,
            difficulty=difficulty,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Could not generate MCQ: "
                f"{exc}"
            ),
        )

    # -----------------------------------------------------
    # 7. Save generated question
    # -----------------------------------------------------

    try:

        from app.models.ai_question import (
            AIGeneratedQuestion,
        )

        question = AIGeneratedQuestion(
            id=uuid.uuid4(),

            learning_content_id=content_id,

            competency_id=None,

            question_text=(
                generated_question[
                    "question_text"
                ]
            ),

            question_type="mcq",

            difficulty=difficulty,

            options=(
                generated_question[
                    "options"
                ]
            ),

            correct_answer=(
                generated_question[
                    "correct_answer"
                ]
            ),

            explanation=(
                generated_question.get(
                    "explanation"
                )
            ),

            source_chunk_ids=[
                str(chunk.id)
                for chunk in chunks
            ],

            generation_model=(
                generated_question.get(
                    "generation_model",
                    "google/flan-t5-base",
                )
            ),

            status="pending",
        )

        db.add(question)

        db.commit()

        db.refresh(question)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "MCQ was generated but could "
                "not be saved: "
                f"{exc}"
            ),
        )

    # -----------------------------------------------------
    # 8. Return MCQ
    # -----------------------------------------------------

    return {
        "id": str(question.id),

        "learning_content_id": str(
            question.learning_content_id
        ),

        "question_text": (
            question.question_text
        ),

        "question_type": (
            question.question_type
        ),

        "difficulty": (
            question.difficulty
        ),

        "options": question.options,

        "correct_answer": (
            question.correct_answer
        ),

        "explanation": (
            question.explanation
        ),

        "source_chunk_ids": (
            question.source_chunk_ids
        ),

        "generation_model": (
            question.generation_model
        ),

        "status": question.status,
    }