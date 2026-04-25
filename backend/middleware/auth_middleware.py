"""
Auth dependency — provides get_current_user for FastAPI route protection.

Usage:
    from middleware.auth_middleware import get_current_user

    @router.get("/protected")
    async def protected(current_user = Depends(get_current_user)):
        ...
"""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from services.auth_service import decode_token, get_user_by_email

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that validates the Bearer JWT token.
    Raises 401 if token is missing or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        logger.warning("🔒 Authentication failed: No credentials provided")
        raise credentials_exception

    logger.debug(f"🔍 Checking token: {credentials.credentials[:20]}...")
    payload = decode_token(credentials.credentials)
    if not payload:
        logger.warning("🔒 Authentication failed: Invalid token")
        raise credentials_exception

    email: str | None = payload.get("sub")
    if not email:
        logger.warning("🔒 Authentication failed: No email in token")
        raise credentials_exception

    logger.debug(f"🔍 Looking up user: {email}")
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"🔒 Authentication failed: User not found: {email}")
        raise credentials_exception

    logger.info(f"✅ Authenticated: {user.email}")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Non-blocking version — returns user or None. Use for soft-protected routes."""
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    email = payload.get("sub")
    return get_user_by_email(db, email) if email else None
