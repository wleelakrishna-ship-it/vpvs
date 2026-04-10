#!/usr/bin/env python3
"""
Test the specific login issue after signup
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def test_login_after_signup_workflow():
    """Test the complete workflow: signup -> login"""
    print("TESTING SIGNUP -> LOGIN WORKFLOW")
    print("="*50)
    
    timestamp = int(time.time())
    
    # Step 1: Create user via signup
    print("Step 1: Creating user via signup...")
    user_data = {
        "username": f"workflow_test_{timestamp}",
        "email": f"workflow_{timestamp}@example.com",
        "phone": "9876543210",
        "dob": "2000-01-01"
    }
    
    try:
        signup_response = requests.post(f"{BASE_URL}/api/profiles/signup", json=user_data, timeout=10)
        print(f"Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 403:
            print("Signup blocked by WAF - this is expected")
            print("Testing with existing user instead...")
            test_existing_user_login()
            return
        elif signup_response.status_code == 200:
            print("Signup successful")
            try:
                signup_data = signup_response.json()
                print(f"Signup Response: {json.dumps(signup_data, indent=2)}")
            except:
                print(f"Signup Raw Response: {signup_response.text}")
        else:
            print(f"Signup failed: {signup_response.text}")
            return
        
        # Step 2: Try to login with the created user
        print(f"\nStep 2: Testing login with created user: {user_data['username']}")
        login_data = {
            "username": user_data["username"],
            "password": "anypassword"  # Password doesn't matter in no-auth
        }
        
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Login Status: {login_response.status_code}")
        print(f"Login Response: {login_response.text[:500]}")
        
        # Analyze the response
        try:
            login_result = login_response.json()
            
            if isinstance(login_result, list):
                print("ERROR: Login response is a list (wrong format)")
                print(f"Response: {json.dumps(login_result, indent=2)}")
                print("This indicates an error response is being returned incorrectly")
            elif isinstance(login_result, dict):
                if "user" in login_result:
                    print("SUCCESS: Login working correctly!")
                    print(f"User: {login_result['user']['username']}")
                elif "error" in login_result:
                    print(f"Login failed with error: {login_result['error']}")
                else:
                    print(f"Unexpected login response: {json.dumps(login_result, indent=2)}")
            else:
                print(f"Unexpected response type: {type(login_result)}")
                
        except json.JSONDecodeError:
            print(f"Could not parse login response as JSON: {login_response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_existing_user_login():
    """Test login with an existing user"""
    print("\nTESTING LOGIN WITH EXISTING USER")
    print("="*50)
    
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "user" in data:
                    print("SUCCESS: Login with existing user works!")
                else:
                    print(f"Unexpected format: {type(data)}")
            except:
                print("Could not parse response")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_nonexistent_user_login():
    """Test login with a non-existent user"""
    print("\nTESTING LOGIN WITH NON-EXISTENT USER")
    print("="*50)
    
    login_data = {
        "username": "nonexistent_user_12345",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text[:500]}")
        
        if response.status_code == 404:
            print("SUCCESS: Non-existent user correctly returns 404")
        elif response.status_code == 200:
            print("WARNING: Non-existent user login succeeded (unexpected)")
        else:
            print(f"Unexpected status: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_login_after_signup_workflow()
    test_existing_user_login()
    test_nonexistent_user_login()
