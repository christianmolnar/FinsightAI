"""
User Authentication API

Endpoints:
  POST /api/auth/register  — create account
  POST /api/auth/login     — get JWT token
  GET  /api/auth/me        — get current user info
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
)
from middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ── Request / Response models ─────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    email: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account and return a JWT token."""
    if get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(db, body.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = create_user(db, email=body.email, username=body.username, password=body.password)
    token = create_access_token({"sub": user.email})

    logger.info(f"New user registered: {user.email}")
    return TokenResponse(access_token=token, username=user.username, email=str(user.email))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(access_token=token, username=user.username, email=str(user.email))


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }
