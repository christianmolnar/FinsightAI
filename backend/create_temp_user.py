#!/usr/bin/env python3
"""Create temporary test user for API testing"""

from sqlalchemy import text
from app.database import SessionLocal
from uuid import UUID

db = SessionLocal()
temp_user_id = str(UUID('00000000-0000-0000-0000-000000000001'))

try:
    # Check if user exists using raw SQL to avoid ORM relationship issues
    result = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": temp_user_id})
    user = result.first()
    
    if not user:
        # Create temp user using raw SQL (only required columns)
        db.execute(text("""
            INSERT INTO users (id, email)
            VALUES (:id, :email)
        """), {
            "id": temp_user_id,
            "email": "temp@test.com"
        })
        db.commit()
        print('✅ Created temp user')
    else:
        print('✅ Temp user already exists')
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
