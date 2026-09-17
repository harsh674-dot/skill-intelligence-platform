# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr, Field
import uuid


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    role_id: uuid.UUID | None = None
    department: str | None = None
    designation: str | None = None
    access_role: str | None = "employee"


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
    department: str | None = None
    designation: str | None = None
    is_active: bool = True