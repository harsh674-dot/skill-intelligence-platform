# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.dialects.postgresql import UUID


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    role_id: UUID | None = None
    department: str | None = None
    designation: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    access_role: str