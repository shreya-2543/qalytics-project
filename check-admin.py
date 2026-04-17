#!/usr/bin/env python3
"""
Diagnostic script to check and fix the admin user seeding issue.
Run this after starting the API to verify the admin is created.
"""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import BOOTSTRAP_ADMIN_USERNAME, BOOTSTRAP_ADMIN_PASSWORD, DATABASE_URL
from backend.database import SessionLocal
from backend import models
from backend.auth import hash_password, verify_password


def check_database():
    """Check if admin user exists in database."""
    print("🔍 Checking admin user in database...\n")
    
    # Get database path from connection string
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ User table doesn't exist - database not initialized")
            return False
        
        cursor.execute("SELECT username, email FROM user WHERE username = ?", (BOOTSTRAP_ADMIN_USERNAME,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Admin user found: {user[0]} ({user[1]})")
            return True
        else:
            print(f"❌ Admin user '{BOOTSTRAP_ADMIN_USERNAME}' not found in database")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        conn.close()


def seed_admin():
    """Manually seed the admin user."""
    print("\n🌱 Attempting to seed admin user...\n")
    
    if not BOOTSTRAP_ADMIN_USERNAME or not BOOTSTRAP_ADMIN_PASSWORD:
        print("❌ BOOTSTRAP_ADMIN_USERNAME or BOOTSTRAP_ADMIN_PASSWORD not configured in .env")
        return False
    
    try:
        db = SessionLocal()
        
        # Check if user already exists
        existing = db.query(models.User).filter_by(username=BOOTSTRAP_ADMIN_USERNAME).first()
        if existing:
            print(f"⚠️  Admin user '{BOOTSTRAP_ADMIN_USERNAME}' already exists")
            # Verify password is correct
            if verify_password(BOOTSTRAP_ADMIN_PASSWORD, existing.hashed_password):
                print("✅ Password is correct")
                return True
            else:
                print("❌ Password is incorrect - need to reset")
                return False
        
        # Create new admin user
        new_admin = models.User(
            username=BOOTSTRAP_ADMIN_USERNAME,
            email="admin@qalytics.dev",
            hashed_password=hash_password(BOOTSTRAP_ADMIN_PASSWORD),
            role="admin",
        )
        db.add(new_admin)
        db.commit()
        print(f"✅ Admin user '{BOOTSTRAP_ADMIN_USERNAME}' created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding admin: {e}")
        return False
    finally:
        db.close()


def test_login():
    """Test login with admin credentials."""
    print("\n🔐 Testing admin login...\n")
    
    if not BOOTSTRAP_ADMIN_USERNAME or not BOOTSTRAP_ADMIN_PASSWORD:
        print("❌ Credentials not configured")
        return False
    
    try:
        db = SessionLocal()
        user = db.query(models.User).filter_by(username=BOOTSTRAP_ADMIN_USERNAME).first()
        
        if not user:
            print(f"❌ User '{BOOTSTRAP_ADMIN_USERNAME}' not found")
            return False
        
        if verify_password(BOOTSTRAP_ADMIN_PASSWORD, user.hashed_password):
            print(f"✅ Login verification successful for '{BOOTSTRAP_ADMIN_USERNAME}'")
            return True
        else:
            print(f"❌ Password mismatch for user '{BOOTSTRAP_ADMIN_USERNAME}'")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("QAlytics Admin User Diagnostic")
    print("=" * 60)
    
    # Step 1: Check database
    db_ok = check_database()
    
    if not db_ok:
        print("\n⚠️  Admin user not found. Attempting to seed...\n")
        if seed_admin():
            print("✅ Admin seeding successful")
        else:
            print("❌ Admin seeding failed")
            sys.exit(1)
    
    # Step 2: Test login
    if test_login():
        print("\n" + "=" * 60)
        print("✅ ALL CHECKS PASSED - Admin is ready")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ LOGIN VERIFICATION FAILED")
        print("=" * 60)
        sys.exit(1)
