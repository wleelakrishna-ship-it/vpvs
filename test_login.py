import requests
import json

# Test API endpoints
base_url = "https://vpvs-1.onrender.com"

def test_login(username, password):
    """Test login with given credentials"""
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login Test for {username}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful!")
            print(f"User ID: {user_data['user']['id']}")
            print(f"Username: {user_data['user']['username']}")
            print(f"Email: {user_data['user']['email']}")
            print(f"Is Admin: {user_data['user']['is_admin']}")
            print(f"Token: {user_data['token'][:20]}...")
            return True
        else:
            print(f"❌ Login failed!")
            return False
            
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return False

def test_posts_with_auth(token):
    """Test posts endpoint with authentication"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(f"{base_url}/api/posts", headers=headers)
        
        print(f"\nPosts Test with Auth:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Posts Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing VPVS Login with Created Users...")
    print("=" * 50)
    
    # Test admin login
    print("\n1. Testing Admin Login...")
    admin_success = test_login("testadmin", "password123")
    
    if admin_success:
        # Extract token and test posts
        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={"username": "testadmin", "password": "password123"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                token = response.json()["token"]
                test_posts_with_auth(token)
        except:
            pass
    
    print("\n" + "=" * 50)
    
    # Test regular user login
    print("\n2. Testing Regular User Login...")
    user_success = test_login("testuser", "password123")
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Admin Login: {'✅ PASS' if admin_success else '❌ FAIL'}")
    print(f"User Login: {'✅ PASS' if user_success else '❌ FAIL'}")
    
    if admin_success and user_success:
        print("\n🎉 All login tests passed! Authentication is working correctly.")
        print("\nYou can now test the frontend with:")
        print("Admin: testadmin / password123")
        print("User: testuser / password123")
    else:
        print("\n⚠️ Some login tests failed. Check the errors above.")
