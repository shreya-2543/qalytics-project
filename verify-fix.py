#!/usr/bin/env python3
"""
Verify that the LoggingMiddleware fix works
Run this AFTER starting the API: uvicorn backend.main:app --reload --port 8000
"""
import requests
import sys
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        resp = requests.get(f"{API_BASE}/api/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API on localhost:8000")
        print("   Make sure API is running: uvicorn backend.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_login():
    """Test login endpoint"""
    try:
        resp = requests.post(
            f"{API_BASE}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if "access_token" in data:
                print("✅ Login passed")
                return data["access_token"]
            else:
                print(f"❌ Login returned no token: {data}")
                return None
        else:
            print(f"❌ Login failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_suites(token):
    """Test suites endpoint"""
    try:
        resp = requests.get(
            f"{API_BASE}/api/suites",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Suites endpoint passed (found {len(data)} suites)")
            return True
        else:
            print(f"❌ Suites failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Suites error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("QAlytics API Verification")
    print("="*60 + "\n")
    
    # Test health
    print("1. Testing health endpoint...")
    if not test_health():
        print("\n❌ API is not responding. Start it with:")
        print("   cd /mnt/d/Shreya/qalytics-project")
        print("   uvicorn backend.main:app --reload --port 8000")
        return 1
    
    time.sleep(1)
    
    # Test login
    print("\n2. Testing login...")
    token = test_login()
    if not token:
        print("\n❌ Login failed. Check admin user exists.")
        return 1
    
    time.sleep(1)
    
    # Test authenticated endpoint
    print("\n3. Testing authenticated endpoint...")
    if not test_suites(token):
        return 1
    
    print("\n" + "="*60)
    print("✅ All verification tests passed!")
    print("="*60)
    print("\nNow you can run the full test suite:")
    print("  pytest automation/ -v")
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
