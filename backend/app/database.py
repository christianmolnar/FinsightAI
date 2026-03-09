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

# Ensure we use psycopg2 driver (handles both postgresql:// and postgres:// variants)
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)
if "+psycopg" in _raw_url and "+psycopg2" not in _raw_url:
    _raw_url = _raw_url.replace("+psycopg", "+psycopg2", 1)
if _raw_url.startswith("postgresql://") and "+psycopg2" not in _raw_url:
    _raw_url = _raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

DATABASE_URL = _raw_url

# Create engine with optimized settings
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "connect_timeout": 10,
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
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

