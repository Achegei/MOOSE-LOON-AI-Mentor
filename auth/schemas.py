"""
Pydantic schemas for authentication endpoints.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserRead(BaseModel):
    """Public user data returned by authentication endpoints."""

    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    skill_level: str

    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    username_or_email: str
    password: str


class Token(BaseModel):
    """JWT token pair returned after login or refresh."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str
