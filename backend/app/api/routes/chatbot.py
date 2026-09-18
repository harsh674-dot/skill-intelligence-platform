import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageAnswer,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionSummary,
)
from app.services.chatbot_service import process_chat_message

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)


@router.post("/message", response_model=ChatMessageAnswer)
def send_message(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the RAG AI chatbot.
    The response is grounded in the employee's personal competency gaps,
    assigned role, recommended courses, and indexed learning content chunks.
    """
    try:
        result = process_chat_message(
            db=db,
            user=current_user,
            message_text=payload.message,
            session_id=payload.session_id,
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(exc)}",
        )


@router.get("/history/{session_id}", response_model=list[ChatMessageResponse])
def get_chat_history(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve full chronological message history for a given chat session.
    Validates that the session belongs to the current user.
    """
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    if session.user_id != current_user.id and current_user.access_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this chat session.",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return messages


@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all chat sessions belonging to the current user.
    """
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    summary_list = []
    for s in sessions:
        count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        summary_list.append(
            ChatSessionSummary(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count,
            )
        )

    return summary_list
