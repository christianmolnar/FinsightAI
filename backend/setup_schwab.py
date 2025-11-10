#!/usr/bin/env python3
"""
Setup script for Charles Schwab API integration
Guides users through the credential setup process
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create the .env file with Schwab API credentials"""
    
    print("🚀 F.Insight AI - Charles Schwab API Setup")
    print("=" * 50)
    print()
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
        print()
    
    print("📋 First, you need to set up your Charles Schwab Developer Account:")
    print("1. Go to https://beta-developer.schwab.com/")
    print("2. Create an account using the SAME EMAIL as your Schwab brokerage account")
    print("3. Create a new Individual Developer App")
    print("4. Set the callback URL to: https://127.0.0.1")
    print("5. Add BOTH API products:")
    print("   - Accounts and Trading Production")
    print("   - Market Data Production")
    print("6. Wait for app status to change to 'Ready for Use' (can take 1-2 days)")
    print("7. Enable TOS (Thinkorswim) for your Schwab account")
    print()
    
    ready = input("Have you completed all the above steps? (y/n): ").lower().strip()
    if ready != 'y':
        print()
        print("📌 Please complete the setup steps above and run this script again.")
        print("   App status must be 'Ready for Use' - 'Approved - Pending' will NOT work!")
        return False
    
    print()
    print("🔑 Now enter your app credentials:")
    print("(You can find these in your Schwab Developer App dashboard)")
    print()
    
    # Get APP_KEY
    while True:
        app_key = input("Enter your APP_KEY (32 characters): ").strip()
        if len(app_key) == 32:
            break
        print(f"❌ Invalid length. APP_KEY should be 32 characters, got {len(app_key)}")
    
    # Get APP_SECRET
    while True:
        app_secret = input("Enter your APP_SECRET (16 characters): ").strip()
        if len(app_secret) == 16:
            break
        print(f"❌ Invalid length. APP_SECRET should be 16 characters, got {len(app_secret)}")
    
    # Callback URL (with default)
    callback_url = input("Enter your CALLBACK_URL [https://127.0.0.1]: ").strip()
    if not callback_url:
        callback_url = "https://127.0.0.1"
    
    print()
    
    # Create .env content
    env_content = f"""# Charles Schwab API Credentials
# KEEP THIS FILE SECURE - DO NOT COMMIT TO VERSION CONTROL
APP_KEY={app_key}
APP_SECRET={app_secret}
CALLBACK_URL={callback_url}

# Database Configuration (already configured)
DATABASE_URL=postgresql://finsight:your_password@localhost:5432/finsight_db
"""
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print()
        
        # Create .gitignore entry if needed
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            with open(".gitignore", "r") as f:
                gitignore_content = f.read()
            
            if ".env" not in gitignore_content:
                with open(".gitignore", "a") as f:
                    f.write("\n# Environment variables\n.env\n")
                print("✅ Added .env to .gitignore for security")
        else:
            with open(".gitignore", "w") as f:
                f.write("# Environment variables\n.env\n")
            print("✅ Created .gitignore with .env entry")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def test_api_connection():
    """Test the API connection"""
    print()
    print("🧪 Testing API Connection...")
    print("-" * 30)
    
    try:
        # Import and test the API
        from app.schwab_api import test_schwab_connection
        
        if test_schwab_connection():
            print()
            print("🎉 SUCCESS! Your Schwab API is working correctly!")
            print()
            print("📊 You can now:")
            print("- Start the backend server: uvicorn app.main:app --reload")
            print("- Access the API at: http://localhost:8000")
            print("- Test market data at: http://localhost:8000/api/market/test-connection")
            print("- View API docs at: http://localhost:8000/docs")
            return True
        else:
            print()
            print("❌ API test failed. Please check your credentials and try again.")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory.")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main():
    """Main setup flow"""
    print()
    
    # Change to the correct directory if needed
    if not Path("app").exists():
        print("❌ Please run this script from the backend directory")
        print("   cd /path/to/your/project/backend")
        print("   python setup_schwab.py")
        sys.exit(1)
    
    # Step 1: Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Step 2: Test connection
    print()
    test_now = input("Do you want to test the API connection now? (y/n): ").lower().strip()
    if test_now == 'y':
        if not test_api_connection():
            print()
            print("💡 Troubleshooting tips:")
            print("1. Make sure your app status is 'Ready for Use'")
            print("2. Verify your credentials are correct")
            print("3. Ensure TOS is enabled on your Schwab account")
            print("4. Check that both APIs are added to your app")
            print("5. Try running the test again after a few minutes")
    
    print()
    print("🎯 Next Steps:")
    print("1. Start your backend server: uvicorn app.main:app --reload")
    print("2. Start your frontend: npm start (from the frontend directory)")
    print("3. Visit http://localhost:3000 to see your trading dashboard")
    print()
    print("📚 For more help, check:")
    print("- Schwab API docs: https://beta-developer.schwab.com/")
    print("- Schwabdev library docs: https://tylerebowers.github.io/Schwabdev/")


if __name__ == "__main__":
    main()
