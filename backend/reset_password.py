#!/usr/bin/env python3
"""
Reset a user's password directly against the Railway database.

Usage:
    python reset_password.py                        # prompts for email + new password
    python reset_password.py --email you@example.com
"""

import sys
import os
import argparse
import getpass

# Allow running from backend/ dir
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from services.auth_service import hash_password, get_user_by_email

def main():
    parser = argparse.ArgumentParser(description="Reset a user password")
    parser.add_argument("--email", help="User email address")
    args = parser.parse_args()

    email = args.email or input("Email: ").strip()
    if not email:
        print("❌ Email is required.")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = get_user_by_email(db, email)
        if not user:
            print(f"❌ No user found with email: {email}")
            sys.exit(1)

        print(f"✅ Found user: {user.username} ({user.email})")

        new_password = getpass.getpass("New password: ")
        confirm     = getpass.getpass("Confirm password: ")

        if new_password != confirm:
            print("❌ Passwords do not match.")
            sys.exit(1)

        if len(new_password) < 8:
            print("❌ Password must be at least 8 characters.")
            sys.exit(1)

        user.password_hash = hash_password(new_password)
        db.commit()
        print(f"✅ Password updated for {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
