"""
JWT Authentication Service

Handles:
- Password hashing (bcrypt)
- JWT token creation and validation
- User lookup and creation
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# --- Config ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_USE_RAILWAY_ENV_VAR")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours


# --- Password utilities (bcrypt direct — no passlib) ---

def _safe_bytes(plain: str) -> bytes:
    """Bcrypt max is 72 bytes — truncate before hashing."""
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_safe_bytes(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_safe_bytes(plain), hashed.encode("utf-8"))


# --- JWT utilities ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns payload dict or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.debug(f"JWT decode failed: {e}")
        return None


# --- User helpers (used by auth router) ---

def get_user_by_email(db: Session, email: str):
    """Return User ORM object or None."""
    from app.models.user import User
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    from app.models.user import User
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, email: str, password: str):
    """Return user if credentials valid, else None."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not hasattr(user, "password_hash") or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, email: str, username: str, password: str):
    """Create a new user with hashed password."""
    from app.models.user import User
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
