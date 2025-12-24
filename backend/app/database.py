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

# Database URL - use Unix socket to avoid network issues
# For PostgreSQL on macOS with Homebrew, the socket is in /tmp
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://finsight:finsight123@/finsight?host=/tmp"
)

# Create engine with optimized settings
# Note: pool_pre_ping=False to avoid connection on import
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=False,  # Don't verify connections on import to avoid hanging
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging
    connect_args={
        "connect_timeout": 5,  # 5 second connection timeout
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

