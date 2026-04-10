#!/usr/bin/env python3
"""
Final comprehensive test of all backend endpoints
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a single endpoint with detailed output"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10, headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10, headers=headers)
        
        print(f"{'='*60}")
        print(f"TEST: {method} {endpoint}")
        print(f"HTTP Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:300]}...")
        
        # Try to parse JSON
        try:
            json_data = response.json()
            print(f"Parsed JSON: {json_data}")
        except:
            print("JSON Parse Failed: Not valid JSON")
        
        return response.status_code, response.text
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None, str(e)

def main():
    print("FINAL BACKEND ENDPOINT TEST")
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test all critical endpoints
    endpoints = [
        ("/api/health", "GET"),
        ("/health", "GET"),
        ("/api", "GET"),
        ("/api/posts", "GET"),
        ("/api/auth/login", "POST", {"username": "testuser", "password": "password123"}),
        ("/api/expenses", "GET"),
        ("/api/expense-groups", "GET"),
        ("/api/posts/test-id/comments", "GET"),
        ("/api/posts/test-id/likes", "GET"),
        ("/api/profiles/signup", "POST", {
            "username": f"test_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "phone": "9876543210",
            "dob": "2000-01-01",
            "is_admin": False
        })
    ]
    
    results = []
    
    for endpoint_data in endpoints:
        if len(endpoint_data) == 2:
            endpoint, method = endpoint_data
            data = None
        else:
            endpoint, method, data = endpoint_data
        
        status, response = test_endpoint(endpoint, method, data)
        results.append({
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "response": response[:100]
        })
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = 0
    total_count = len(results)
    
    for result in results:
        if result["status"] and 200 <= result["status"] < 300:
            print(f"  {result['method']} {result['endpoint']}: {result['status']} - SUCCESS")
            success_count += 1
        elif result["status"] and result["status"] == 401:
            print(f"  {result['method']} {result['endpoint']}: {result['status']} - AUTH REQUIRED (Expected)")
        elif result["status"] and result["status"] == 403:
            print(f"  {result['method']} {result['endpoint']}: {result['status']} - FORBIDDEN (WAF)")
        else:
            print(f"  {result['method']} {result['endpoint']}: {result['status']} - ISSUE")
    
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print("\nExpected Status:")
    print("- Health endpoints: Should be 200 (fixed)")
    print("- Expense groups: Should be 200 (auth removed)")
    print("- Comments/Likes: Should be 200 (order method fixed)")
    print("- Signup: Should be 403 (WAF blocking)")

if __name__ == "__main__":
    main()
