#!/usr/bin/env python3
"""
Debug authentication response format issue
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def debug_auth_response():
    """Debug what the auth response actually contains"""
    print("🔍 DEBUGGING AUTHENTICATION RESPONSE")
    print("="*60)
    
    # Test expenses endpoint without auth
    print("\n1. Testing /api/expenses WITHOUT authentication:")
    try:
        response = requests.get(f"{BASE_URL}/api/expenses", timeout=10)
        print(f"   HTTP Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text[:500]}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"   Parsed JSON: {json_data}")
        except:
            print(f"   JSON Parse Failed: Not valid JSON")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with a fake token
    print("\n2. Testing /api/expenses WITH fake token:")
    try:
        headers = {"Authorization": "Bearer fake-token-12345"}
        response = requests.get(f"{BASE_URL}/api/expenses", headers=headers, timeout=10)
        print(f"   HTTP Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text[:500]}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"   Parsed JSON: {json_data}")
        except:
            print(f"   JSON Parse Failed: Not valid JSON")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test health endpoint for comparison
    print("\n3. Testing /api/health for comparison:")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"   HTTP Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text[:500]}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"   Parsed JSON: {json_data}")
        except:
            print(f"   JSON Parse Failed: Not valid JSON")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test the base /api endpoint
    print("\n4. Testing /api for comparison:")
    try:
        response = requests.get(f"{BASE_URL}/api", timeout=10)
        print(f"   HTTP Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response Body: {response.text[:500]}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"   Parsed JSON: {json_data}")
        except:
            print(f"   JSON Parse Failed: Not valid JSON")
            
    except Exception as e:
        print(f"   Error: {e}")

def main():
    print("🚀 AUTHENTICATION RESPONSE DEBUG")
    print(f"🌐 Target: {BASE_URL}")
    print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    debug_auth_response()
    
    print("\n" + "="*60)
    print("📊 ANALYSIS:")
    print("• Check if HTTP status is actually 401 or 200")
    print("• Check if response body contains error or data")
    print("• Compare with working endpoints")
    print("• Identify exact response format issue")

if __name__ == "__main__":
    main()
