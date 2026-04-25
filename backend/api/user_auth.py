"""
User Authentication API

Endpoints:
  POST /api/auth/register         — create account
  POST /api/auth/login            — get JWT token
  GET  /api/auth/me               — get current user info
  POST /api/auth/change-password  — change password (requires current password)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from services.auth_service import (
    authenticate_user,
    create_user,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
    verify_password,
    hash_password,
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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    logger.info(f"📝 Registration attempt: {body.email}")
    
    # Check if user already exists
    existing_user = get_user_by_email(db, body.email)
    if existing_user:
        logger.warning(f"⚠️  Registration failed - email already exists: {body.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = get_user_by_username(db, body.username)
    if existing_username:
        logger.warning(f"⚠️  Registration failed - username already exists: {body.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user = create_user(db, body.email, body.username, body.password)
    token = create_access_token({"sub": user.email})
    logger.info(f"✅ User registered successfully: {user.email}")
    
    return TokenResponse(access_token=token, username=user.username, email=str(user.email))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    logger.info(f"🔐 Login attempt: {body.email}")
    
    user = authenticate_user(db, body.email, body.password)
    if not user:
        logger.warning(f"🔒 Login failed for: {body.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})
    logger.info(f"✅ User logged in successfully: {user.email}")
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


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    body: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password — requires the current password for verification."""
    if not current_user.password_hash or not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    current_user.password_hash = hash_password(body.new_password)
    db.commit()
    logger.info(f"Password changed for {current_user.email}")
    return {"message": "Password updated successfully"}
