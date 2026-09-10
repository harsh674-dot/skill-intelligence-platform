from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.competency import RoleCompetency, UserCompetency
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new employee account.
    """

    # Check whether the email is already registered.
    result = db.execute(
        select(User).where(User.email == data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # Create a new employee.
    selected_role_id = data.role_id
    if selected_role_id is None:
        default_role = db.scalar(
            select(Role).where(Role.is_active == True).order_by(Role.name).limit(1)
        )
        if default_role:
            selected_role_id = default_role.id

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        access_role="employee",
        department=data.department,
        designation=data.designation,
        job_role_id=selected_role_id,
        is_active=True,
    )

    db.add(user)
    db.flush()

    if selected_role_id:
        role_competencies = db.scalars(
            select(RoleCompetency).where(RoleCompetency.role_id == selected_role_id)
        ).all()

        for rc in role_competencies:
            user_competency = UserCompetency(
                user_id=user.id,
                competency_id=rc.competency_id,
                current_level=1,
                source="initial",
            )
            db.add(user_competency)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        access_role=user.access_role,
    )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    """

    result = db.execute(
        select(User).where(User.email == data.email)
    )

    user = result.scalar_one_or_none()

    # Do not reveal whether the email exists.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # Verify password against stored hash.
    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # Prevent inactive accounts from logging in.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Generate JWT.
    access_token = create_access_token(
        user_id=str(user.id),
        access_role=user.access_role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return information about the currently authenticated user.
    """

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        access_role=current_user.access_role,
    )