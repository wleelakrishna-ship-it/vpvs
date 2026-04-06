#!/usr/bin/env python3
"""
Simple backend test to check if endpoints are accessible
"""

import requests
import json

BASE_URL = "https://vpvs-backend.onrender.com"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10, headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10, headers=headers)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        print()
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {str(e)}")
        print()
        return None

def main():
    print("🚀 SIMPLE BACKEND TEST")
    print(f"🌐 Testing: {BASE_URL}")
    print("="*50)
    
    # Test basic endpoints
    test_endpoint("/")
    test_endpoint("/api")
    test_endpoint("/api/health")
    test_endpoint("/api/posts")
    test_endpoint("/api/auth/login", "POST", {"username": "test", "password": "test"})
    
    print("="*50)
    print("📊 TEST COMPLETE")

if __name__ == "__main__":
    main()
