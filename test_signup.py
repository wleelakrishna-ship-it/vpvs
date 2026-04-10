#!/usr/bin/env python3
"""
Test signup functionality
"""

import requests
import time
import json

BASE_URL = "https://vpvs-1.onrender.com"

def test_signup():
    """Test the signup endpoint"""
    print("Testing Signup Functionality")
    print("="*40)
    
    # Generate unique test data
    timestamp = int(time.time())
    test_data = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "phone": "9876543210",
        "dob": "2000-01-01",
        "is_admin": False
    }
    
    print(f"Test Data: {test_data}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/profiles/signup", json=test_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                if "profile" in data:
                    profile = data["profile"]
                    print(f"Created Profile ID: {profile.get('id')}")
                    print(f"Username: {profile.get('username')}")
                    print(f"Email: {profile.get('email')}")
                    print("SUCCESS: Signup working correctly!")
                else:
                    print("WARNING: No profile data in response")
            except json.JSONDecodeError:
                print(f"Raw Response: {response.text}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_login_after_signup():
    """Test login with the created user"""
    print("\nTesting Login After Signup")
    print("="*40)
    
    timestamp = int(time.time())
    login_data = {
        "username": f"testuser_{timestamp}",
        "password": "password123"
    }
    
    try:
        # First create user
        signup_data = {
            "username": login_data["username"],
            "email": f"{login_data['username']}@example.com",
            "phone": "9876543210",
            "dob": "2000-01-01"
        }
        
        print("Creating user...")
        signup_response = requests.post(f"{BASE_URL}/api/profiles/signup", json=signup_data, timeout=10)
        print(f"Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            print("User created successfully, testing login...")
            
            # Test login
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print(f"Login Response: {json.dumps(login_data, indent=2)}")
                print("SUCCESS: Login working after signup!")
            else:
                print(f"Login Failed: {login_response.text}")
        else:
            print(f"Signup Failed: {signup_response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_profiles_list():
    """Test getting all profiles"""
    print("\nTesting Profiles List")
    print("="*40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/profiles", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "profiles" in data:
                profiles = data["profiles"]
                print(f"Found {len(profiles)} profiles")
                
                if profiles:
                    print("Sample Profile:")
                    print(json.dumps(profiles[0], indent=2))
                else:
                    print("No profiles found")
            else:
                print("No profiles key in response")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_signup()
    test_login_after_signup()
    test_profiles_list()
