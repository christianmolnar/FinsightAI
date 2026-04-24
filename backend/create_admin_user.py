#!/usr/bin/env python3
"""
Create admin user account for f.Insight.AI

Usage:
    python create_admin_user.py <email> <username> <password>
    
Example:
    python create_admin_user.py admin@finsight.ai admin MyPassword123!
"""

import sys
from sqlalchemy import text
from app.database import SessionLocal
from services.auth_service import hash_password

def create_admin(email, username, password):
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        sys.exit(1)
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    db = SessionLocal()
    try:
        # Check if user exists
        result = db.execute(
            text("SELECT id FROM users WHERE email = :email"), 
            {"email": email}
        )
        existing = result.first()
        
        if existing:
            print(f"❌ User with email {email} already exists")
            sys.exit(1)
        
        # Insert user
        db.execute(
            text("""
                INSERT INTO users (email, username, password_hash)
                VALUES (:email, :username, :password_hash)
            """),
            {
                "email": email,
                "username": username,
                "password_hash": password_hash
            }
        )
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ Admin user created successfully!")
        print("=" * 60)
        print(f"Email:    {email}")
        print(f"Username: {username}")
        print()
        print("You can now log in at:")
        print("  https://frontend-pi-kohl-57.vercel.app")
        print("  or http://localhost:3000 (if running locally)")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin_user.py <email> <username> <password>")
        print("Example: python create_admin_user.py admin@finsight.ai admin MyPassword123!")
        sys.exit(1)
    
    email = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    create_admin(email, username, password)
