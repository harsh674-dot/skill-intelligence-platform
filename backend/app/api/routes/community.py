import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.community import Post, Comment, Like
from app.schemas.community import (
    PostCreate,
    PostResponse,
    PostDetailResponse,
    CommentCreate,
    CommentResponse,
    LikeToggleResponse,
    AuthorSummary,
)

router = APIRouter(
    prefix="/community",
    tags=["community"],
)


def _build_post_response(post: Post, current_user: User, db: Session) -> PostResponse:
    likes_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar() or 0
    comments_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar() or 0
    has_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first() is not None

    author_summary = AuthorSummary(
        id=post.author.id,
        full_name=post.author.full_name,
        email=post.author.email,
        designation=post.author.designation,
        department=post.author.department,
        access_role=post.author.access_role,
    )

    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        author=author_summary,
        title=post.title,
        body=post.body,
        tags=post.tags or [],
        created_at=post.created_at,
        updated_at=post.updated_at,
        likes_count=likes_count,
        comments_count=comments_count,
        has_liked=has_liked,
    )


@router.get("/posts", response_model=list[PostResponse])
def list_posts(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in title or body"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List community posts with like and comment counts.
    Supports tag filtering and keyword search.
    """
    query = db.query(Post)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter((Post.title.ilike(s)) | (Post.body.ilike(s)))

    posts = query.order_by(Post.created_at.desc()).all()

    # If tag filter, filter posts containing tag
    if tag:
        tag_clean = tag.strip().lower()
        posts = [
            p for p in posts
            if any(str(t).lower() == tag_clean for t in (p.tags or []))
        ]

    return [_build_post_response(p, current_user, db) for p in posts]


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new community discussion post. All roles can post.
    """
    post = Post(
        author_id=current_user.id,
        title=payload.title.strip(),
        body=payload.body.strip(),
        tags=payload.tags,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return _build_post_response(post, current_user, db)


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve single post with all threaded comments.
    """
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    base_response = _build_post_response(post, current_user, db)

    comment_responses = []
    for c in post.comments:
        c_author = AuthorSummary(
            id=c.author.id,
            full_name=c.author.full_name,
            email=c.author.email,
            designation=c.author.designation,
            department=c.author.department,
            access_role=c.author.access_role,
        )
        comment_responses.append(
            CommentResponse(
                id=c.id,
                post_id=c.post_id,
                author_id=c.author_id,
                author=c_author,
                body=c.body,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return PostDetailResponse(
        **base_response.model_dump(),
        comments=comment_responses,
    )


@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a post. Post author or System Admin can delete/moderate.
    """
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    if post.author_id != current_user.id and current_user.access_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author or an admin can delete this post.",
        )

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully.", "post_id": post_id}


@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: uuid.UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a comment to a post. All roles can comment.
    """
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    comment = Comment(
        post_id=post.id,
        author_id=current_user.id,
        body=payload.body.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    c_author = AuthorSummary(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        designation=current_user.designation,
        department=current_user.department,
        access_role=current_user.access_role,
    )

    return CommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author=c_author,
        body=comment.body,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a comment. Comment author or System Admin can delete/moderate.
    """
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )

    if comment.author_id != current_user.id and current_user.access_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author or an admin can delete this comment.",
        )

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully.", "comment_id": comment_id}


@router.post("/posts/{post_id}/like", response_model=LikeToggleResponse)
def toggle_like(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Toggle like on a post for the current user.
    """
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    existing_like = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )

    if existing_like:
        db.delete(existing_like)
        db.commit()
        liked = False
    else:
        new_like = Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        liked = True

    total_likes = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0

    return LikeToggleResponse(
        post_id=post_id,
        liked=liked,
        likes_count=total_likes,
    )
