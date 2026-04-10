#!/usr/bin/env python3
"""
Debug signup and login issues
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def test_signup_detailed():
    """Test signup with detailed debugging"""
    print("DETAILED SIGNUP TEST")
    print("="*50)
    
    timestamp = int(time.time())
    signup_data = {
        "username": f"debug_user_{timestamp}",
        "email": f"debug_{timestamp}@example.com",
        "phone": "9876543210",
        "dob": "2000-01-01",
        "is_admin": False
    }
    
    print(f"Signup Data: {json.dumps(signup_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/profiles/signup", json=signup_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}")
        
        if "403" in response.text:
            print("WAF BLOCKED - This is a Supabase WAF issue")
            print("Solution: Add Render IPs to Supabase WAF allowlist")
        elif response.status_code == 200:
            try:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            except:
                print("Could not parse JSON response")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_login_detailed():
    """Test login with detailed debugging"""
    print("\nDETAILED LOGIN TEST")
    print("="*50)
    
    # Test with existing user
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    print(f"Login Data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}")
        
        try:
            data = response.json()
            print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            
            # Check if response is in the wrong format
            if isinstance(data, list) and len(data) == 2:
                print("ERROR: Response is in wrong format [error, status_code]")
                print("This suggests the endpoint is returning an error response incorrectly")
            elif isinstance(data, dict) and "user" in data:
                print("SUCCESS: Login response format is correct")
            else:
                print("WARNING: Unexpected response format")
                
        except json.JSONDecodeError:
            print("Could not parse JSON response")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_create_user_then_login():
    """Create a user then test login"""
    print("\nCREATE USER THEN LOGIN TEST")
    print("="*50)
    
    timestamp = int(time.time())
    
    # Step 1: Create user
    print("Step 1: Creating user...")
    user_data = {
        "username": f"login_test_{timestamp}",
        "email": f"login_test_{timestamp}@example.com",
        "phone": "9876543210",
        "dob": "2000-01-01"
    }
    
    try:
        signup_response = requests.post(f"{BASE_URL}/api/profiles/signup", json=user_data, timeout=10)
        print(f"Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            print("User created successfully")
            
            # Step 2: Test login
            print("\nStep 2: Testing login...")
            login_data = {
                "username": user_data["username"],
                "password": "anypassword"  # Password doesn't matter in no-auth
            }
            
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
            print(f"Login Status: {login_response.status_code}")
            print(f"Login Response: {login_response.text[:500]}")
            
            if login_response.status_code == 200:
                try:
                    login_data = login_response.json()
                    if isinstance(login_data, dict) and "user" in login_data:
                        print("SUCCESS: Login working correctly!")
                    else:
                        print("ERROR: Login response format issue")
                except:
                    print("ERROR: Could not parse login response")
            else:
                print(f"ERROR: Login failed with status {login_response.status_code}")
        else:
            print(f"ERROR: User creation failed with status {signup_response.status_code}")
            if "403" in signup_response.text:
                print("This is due to Supabase WAF blocking")
                
    except Exception as e:
        print(f"Error: {str(e)}")

def test_profiles_endpoint():
    """Test profiles endpoint"""
    print("\nPROFILES ENDPOINT TEST")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/profiles", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 404:
            print("Profiles endpoint not found - this needs to be added")
        elif response.status_code == 200:
            try:
                data = response.json()
                if "profiles" in data:
                    print(f"Found {len(data['profiles'])} profiles")
                else:
                    print("Profiles endpoint working but no profiles key")
            except:
                print("Could not parse profiles response")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_signup_detailed()
    test_login_detailed()
    test_create_user_then_login()
    test_profiles_endpoint()
