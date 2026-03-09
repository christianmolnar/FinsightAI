"""
Database Configuration
SQLAlchemy setup and session management for the FInsightAI application.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL
# Railway provides postgresql:// — normalize to psycopg2 driver prefix
_raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql://finsight:finsight123@localhost:5432/finsight"
)

# Normalize driver prefix (Railway provides postgresql://, SQLAlchemy needs psycopg2)
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)
if "+psycopg" in _raw_url and "+psycopg2" not in _raw_url:
    _raw_url = _raw_url.replace("+psycopg", "+psycopg2", 1)
if _raw_url.startswith("postgresql://") and "+psycopg2" not in _raw_url:
    _raw_url = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Strip sslmode from URL — we pass it via connect_args instead (more reliable with psycopg2)
import re
_raw_url = re.sub(r'[?&]sslmode=[^&]*', '', _raw_url).rstrip('?').rstrip('&')

DATABASE_URL = _raw_url

# Create engine — small pool, SSL via connect_args, no pre-ping (we check at startup)
engine = create_engine(
    DATABASE_URL,
    pool_size=2,
    max_overflow=5,
    pool_pre_ping=False,
    pool_recycle=1800,
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require",
        "keepalives": 1,
        "keepalives_idle": 5,
        "keepalives_interval": 2,
        "keepalives_count": 3,
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Use with FastAPI Depends() for automatic session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this after all models are imported.
    """
    from app import models  # Import models to register them with Base
    Base.metadata.create_all(bind=engine)


def check_connection():
    """
    Check if database connection is working.
    Returns True if successful, False otherwise.
    """
    from sqlalchemy import text
    import threading

    result = [False]
    error = [None]

    def _check():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result[0] = True
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=_check, daemon=True)
    t.start()
    t.join(timeout=8)  # Give up after 8 seconds — never block the app

    if not t.is_alive() and result[0]:
        return True
    print(f"Database connection failed or timed out: {error[0]}")
    return False

