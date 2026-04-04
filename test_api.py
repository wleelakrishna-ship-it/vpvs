import requests
import json

# Test API endpoints
base_url = "https://vpvs-1.onrender.com"

def test_health():
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

def test_signup():
    try:
        signup_data = {
            "username": "testadmin",
            "email": "testadmin@test.com", 
            "password": "password123",
            "phone": "1234567890",
            "dob": "2000-01-01",
            "is_admin": True
        }
        
        response = requests.post(
            f"{base_url}/api/profiles/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Signup Status: {response.status_code}")
        print(f"Signup Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Signup Error: {e}")
        return False

def test_login():
    try:
        login_data = {
            "username": "testadmin",
            "password": "password123"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Login Error: {e}")
        return False

def test_posts():
    try:
        response = requests.get(f"{base_url}/api/posts")
        print(f"Posts Status: {response.status_code}")
        print(f"Posts Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Posts Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing VPVS API...")
    print("=" * 50)
    
    print("1. Testing Health Check...")
    health_ok = test_health()
    
    print("\n2. Testing Signup...")
    signup_ok = test_signup()
    
    print("\n3. Testing Login...")
    login_ok = test_login()
    
    print("\n4. Testing Posts...")
    posts_ok = test_posts()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Signup: {'✅ PASS' if signup_ok else '❌ FAIL'}")
    print(f"Login: {'✅ PASS' if login_ok else '❌ FAIL'}")
    print(f"Posts: {'✅ PASS' if posts_ok else '❌ FAIL'}")
    
    if all([health_ok, signup_ok, login_ok, posts_ok]):
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
