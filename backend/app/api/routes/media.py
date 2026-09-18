import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.learning import LearningContent
from app.models.user import User
from app.services.speech_to_text import SpeechToTextService

router = APIRouter(
    prefix="/media",
    tags=["Media & Speech-to-Text"],
)


@router.get("/transcribe/status")
def speech_status(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """Check speech-to-text service status."""
    service = SpeechToTextService()
    return {
        "available": service.load_model(),
        "fallback_available": True,
        "model": os.environ.get("WHISPER_MODEL", "base"),
    }


@router.post("/transcribe", status_code=status.HTTP_202_ACCEPTED)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Query("en"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Transcribe audio/video using Whisper (with fallback)."""
    service = SpeechToTextService()

    upload_dir = "uploads/media"
    os.makedirs(upload_dir, exist_ok=True)
    upload_path = f"{upload_dir}/{uuid.uuid4().hex}_{file.filename}"

    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    try:
        result = service.transcribe(upload_path, language)
        return {
            "transcription_id": str(uuid.uuid4()),
            "filename": file.filename,
            "text": result.get("text", ""),
            "language": result.get("language", language),
            "segments": result.get("segments", []),
            "fallback": result.get("metadata", {}).get("fallback", False),
            "error": result.get("error"),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {exc}",
        )
