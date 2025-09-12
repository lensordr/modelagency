#!/usr/bin/env python3
"""Quick test to verify authentication setup"""

def test_imports():
    try:
        from jose import jwt
        from passlib.context import CryptContext
        from auth import create_access_token, verify_password, get_password_hash
        from models import User
        print("[OK] All authentication modules imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_password_hashing():
    try:
        from auth import get_password_hash, verify_password
        password = "test123"
        hashed = get_password_hash(password)
        is_valid = verify_password(password, hashed)
        if is_valid:
            print("[OK] Password hashing works correctly")
            return True
        else:
            print("[ERROR] Password verification failed")
            return False
    except Exception as e:
        print(f"[ERROR] Password hashing error: {e}")
        return False

def test_jwt_token():
    try:
        from auth import create_access_token, verify_token
        token = create_access_token({"sub": "admin", "role": "admin"})
        payload = verify_token(token)
        if payload.get("sub") == "admin":
            print("[OK] JWT token creation and verification works")
            return True
        else:
            print("[ERROR] JWT token verification failed")
            return False
    except Exception as e:
        print(f"[ERROR] JWT token error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Restaurant Authentication System")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_password_hashing,
        test_jwt_token
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\nAuthentication system is ready!")
        print("\nTo start the server:")
        print("1. Run: python start_server.py")
        print("2. Visit: http://localhost:8001/business/login")
        print("3. Login with: admin / rrares")
    else:
        print("\nSome tests failed. Check the errors above.")