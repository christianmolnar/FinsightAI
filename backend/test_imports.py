#!/usr/bin/env python3
"""
Minimal import test to identify where the hang occurs
"""
import sys

print("Step 1: Testing basic imports...")
import os
print("✓ os imported")

print("\nStep 2: Testing SQLAlchemy...")
from sqlalchemy import create_engine
print("✓ sqlalchemy imported")

print("\nStep 3: Testing dotenv...")
from dotenv import load_dotenv
load_dotenv()
print("✓ dotenv loaded")

print("\nStep 4: Testing app.database (WITHOUT connection)...")
# Don't import engine yet, just the Base
from sqlalchemy.ext.declarative import declarative_base
print("✓ declarative_base imported")

print("\nStep 5: Creating test engine with pool_pre_ping=False...")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finsight:finsight123@127.0.0.1:5432/finsight")
print(f"Database URL: {DATABASE_URL}")

test_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=False,
    echo=False,
    connect_args={"connect_timeout": 5}
)
print("✓ Engine created (no connection attempted yet)")

print("\nStep 6: Testing actual connection...")
try:
    with test_engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✓ Database connection successful!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)

print("\nStep 7: Import app.database module...")
from app.database import Base, engine
print("✓ app.database imported")

print("\nStep 8: Import User model...")
from app.models.user import User
print("✓ User model imported")

print("\n✅ ALL TESTS PASSED!")
