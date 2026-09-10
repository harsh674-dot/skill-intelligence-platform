from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.services.vector_search import search_content


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/learning")
def search_learning_content(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    results = search_content(
        db=db,
        query=q,
        limit=limit,
    )

    return {
        "query": q,
        "result_count": len(results),
        "results": [
            {
                "chunk_id": str(result.id),
                "learning_content_id": str(
                    result.learning_content_id
                ),
                "chunk_index": result.chunk_index,
                "similarity": float(result.similarity),
                "text": result.chunk_text,
            }
            for result in results
        ],
    }