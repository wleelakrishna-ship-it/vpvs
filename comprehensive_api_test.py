#!/usr/bin/env python3
"""
Comprehensive API test with proper data validation
"""

import requests
import json
import time
from uuid import uuid4

BASE_URL = "https://vpvs-1.onrender.com"

def test_api_with_validation():
    """Test all APIs with proper response validation"""
    print("COMPREHENSIVE API TEST WITH DATA VALIDATION")
    print("="*60)
    
    results = []
    
    # Test 1: Health Check
    print("\n1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "healthy":
                print("  Health Check: PASS")
                results.append({"endpoint": "/api/health", "status": "PASS"})
            else:
                print(f"  Health Check: FAIL - Invalid response: {data}")
                results.append({"endpoint": "/api/health", "status": "FAIL", "error": "Invalid response"})
        else:
            print(f"  Health Check: FAIL - HTTP {response.status_code}")
            results.append({"endpoint": "/api/health", "status": "FAIL", "error": f"HTTP {response.status_code}"})
    except Exception as e:
        print(f"  Health Check: ERROR - {str(e)}")
        results.append({"endpoint": "/api/health", "status": "ERROR", "error": str(e)})
    
    # Test 2: Posts
    print("\n2. Testing Posts")
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "posts" in data and isinstance(data["posts"], list):
                print(f"  Posts: PASS - Found {len(data['posts'])} posts")
                results.append({"endpoint": "/api/posts", "status": "PASS", "data": f"{len(data['posts'])} posts"})
            else:
                print(f"  Posts: FAIL - Invalid response: {data}")
                results.append({"endpoint": "/api/posts", "status": "FAIL", "error": "Invalid response"})
        else:
            print(f"  Posts: FAIL - HTTP {response.status_code}")
            results.append({"endpoint": "/api/posts", "status": "FAIL", "error": f"HTTP {response.status_code}"})
    except Exception as e:
        print(f"  Posts: ERROR - {str(e)}")
        results.append({"endpoint": "/api/posts", "status": "ERROR", "error": str(e)})
    
    # Test 3: Login
    print("\n3. Testing Login")
    try:
        login_data = {"username": "testuser", "password": "password123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "user" in data and "token" in data:
                token = data["token"]
                print(f"  Login: PASS - User: {data['user']['username']}")
                results.append({"endpoint": "/api/auth/login", "status": "PASS", "token": token[:20] + "..."})
                
                # Test authenticated endpoints with token
                test_authenticated_endpoints(token, results)
            else:
                print(f"  Login: FAIL - Invalid response: {data}")
                results.append({"endpoint": "/api/auth/login", "status": "FAIL", "error": "Invalid response"})
        else:
            print(f"  Login: FAIL - HTTP {response.status_code}")
            results.append({"endpoint": "/api/auth/login", "status": "FAIL", "error": f"HTTP {response.status_code}"})
    except Exception as e:
        print(f"  Login: ERROR - {str(e)}")
        results.append({"endpoint": "/api/auth/login", "status": "ERROR", "error": str(e)})
    
    # Test 4: Expense Groups (without auth)
    print("\n4. Testing Expense Groups (no auth)")
    try:
        response = requests.get(f"{BASE_URL}/api/expense-groups", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "groups" in data and isinstance(data["groups"], list):
                print(f"  Expense Groups: PASS - Found {len(data['groups'])} groups")
                results.append({"endpoint": "/api/expense-groups", "status": "PASS", "data": f"{len(data['groups'])} groups"})
            elif "error" in data:
                print(f"  Expense Groups: FAIL - Auth error: {data['error']}")
                results.append({"endpoint": "/api/expense-groups", "status": "FAIL", "error": data['error']})
            else:
                print(f"  Expense Groups: FAIL - Invalid response: {data}")
                results.append({"endpoint": "/api/expense-groups", "status": "FAIL", "error": "Invalid response"})
        else:
            print(f"  Expense Groups: FAIL - HTTP {response.status_code}")
            results.append({"endpoint": "/api/expense-groups", "status": "FAIL", "error": f"HTTP {response.status_code}"})
    except Exception as e:
        print(f"  Expense Groups: ERROR - {str(e)}")
        results.append({"endpoint": "/api/expense-groups", "status": "ERROR", "error": str(e)})
    
    # Test 5: Comments with valid post ID
    print("\n5. Testing Comments")
    try:
        # First get a valid post ID
        posts_response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        if posts_response.status_code == 200:
            posts_data = posts_response.json()
            if posts_data.get("posts") and len(posts_data["posts"]) > 0:
                post_id = posts_data["posts"][0]["id"]
                print(f"  Using post ID: {post_id}")
                
                # Test comments
                response = requests.get(f"{BASE_URL}/api/posts/{post_id}/comments", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "comments" in data and isinstance(data["comments"], list):
                        print(f"  Comments: PASS - Found {len(data['comments'])} comments")
                        results.append({"endpoint": f"/api/posts/{post_id}/comments", "status": "PASS", "data": f"{len(data['comments'])} comments"})
                    elif "error" in data:
                        print(f"  Comments: FAIL - Error: {data['error']}")
                        results.append({"endpoint": f"/api/posts/{post_id}/comments", "status": "FAIL", "error": data['error']})
                    else:
                        print(f"  Comments: FAIL - Invalid response: {data}")
                        results.append({"endpoint": f"/api/posts/{post_id}/comments", "status": "FAIL", "error": "Invalid response"})
                else:
                    print(f"  Comments: FAIL - HTTP {response.status_code}")
                    results.append({"endpoint": f"/api/posts/{post_id}/comments", "status": "FAIL", "error": f"HTTP {response.status_code}"})
            else:
                print("  Comments: FAIL - No posts available")
                results.append({"endpoint": "/api/posts/{id}/comments", "status": "FAIL", "error": "No posts available"})
        else:
            print("  Comments: FAIL - Could not get posts")
            results.append({"endpoint": "/api/posts/{id}/comments", "status": "FAIL", "error": "Could not get posts"})
    except Exception as e:
        print(f"  Comments: ERROR - {str(e)}")
        results.append({"endpoint": "/api/posts/{id}/comments", "status": "ERROR", "error": str(e)})
    
    # Test 6: Likes with valid post ID
    print("\n6. Testing Likes")
    try:
        # First get a valid post ID
        posts_response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        if posts_response.status_code == 200:
            posts_data = posts_response.json()
            if posts_data.get("posts") and len(posts_data["posts"]) > 0:
                post_id = posts_data["posts"][0]["id"]
                print(f"  Using post ID: {post_id}")
                
                # Test likes
                response = requests.get(f"{BASE_URL}/api/posts/{post_id}/likes", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "likes" in data and isinstance(data["likes"], list):
                        print(f"  Likes: PASS - Found {len(data['likes'])} likes")
                        results.append({"endpoint": f"/api/posts/{post_id}/likes", "status": "PASS", "data": f"{len(data['likes'])} likes"})
                    elif "error" in data:
                        print(f"  Likes: FAIL - Error: {data['error']}")
                        results.append({"endpoint": f"/api/posts/{post_id}/likes", "status": "FAIL", "error": data['error']})
                    else:
                        print(f"  Likes: FAIL - Invalid response: {data}")
                        results.append({"endpoint": f"/api/posts/{post_id}/likes", "status": "FAIL", "error": "Invalid response"})
                else:
                    print(f"  Likes: FAIL - HTTP {response.status_code}")
                    results.append({"endpoint": f"/api/posts/{post_id}/likes", "status": "FAIL", "error": f"HTTP {response.status_code}"})
            else:
                print("  Likes: FAIL - No posts available")
                results.append({"endpoint": "/api/posts/{id}/likes", "status": "FAIL", "error": "No posts available"})
        else:
            print("  Likes: FAIL - Could not get posts")
            results.append({"endpoint": "/api/posts/{id}/likes", "status": "FAIL", "error": "Could not get posts"})
    except Exception as e:
        print(f"  Likes: ERROR - {str(e)}")
        results.append({"endpoint": "/api/posts/{id}/likes", "status": "ERROR", "error": str(e)})
    
    return results

def test_authenticated_endpoints(token, results):
    """Test endpoints that require authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n  Testing Authenticated Endpoints:")
    
    # Test expenses with auth
    try:
        response = requests.get(f"{BASE_URL}/api/expenses", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"    Expenses (auth): PASS - Found {len(data)} expenses")
                results.append({"endpoint": "/api/expenses", "status": "PASS", "data": f"{len(data)} expenses"})
            else:
                print(f"    Expenses (auth): FAIL - Invalid response: {data}")
                results.append({"endpoint": "/api/expenses", "status": "FAIL", "error": "Invalid response"})
        else:
            print(f"    Expenses (auth): FAIL - HTTP {response.status_code}")
            results.append({"endpoint": "/api/expenses", "status": "FAIL", "error": f"HTTP {response.status_code}"})
    except Exception as e:
        print(f"    Expenses (auth): ERROR - {str(e)}")
        results.append({"endpoint": "/api/expenses", "status": "ERROR", "error": str(e)})

def generate_report(results):
    """Generate comprehensive report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE API TEST REPORT")
    print("="*60)
    
    pass_count = len([r for r in results if r["status"] == "PASS"])
    fail_count = len([r for r in results if r["status"] == "FAIL"])
    error_count = len([r for r in results if r["status"] == "ERROR"])
    total_count = len(results)
    
    print(f"\nSUMMARY:")
    print(f"  Total Tests: {total_count}")
    print(f"  Passed: {pass_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Errors: {error_count}")
    print(f"  Success Rate: {(pass_count/total_count*100):.1f}%" if total_count > 0 else "N/A")
    
    print(f"\nDETAILED RESULTS:")
    for result in results:
        status_icon = "  " if result["status"] == "PASS" else "  " if result["status"] == "FAIL" else "  "
        print(f"{status_icon} {result['endpoint']}: {result['status']}")
        if "data" in result:
            print(f"    Data: {result['data']}")
        if "error" in result:
            print(f"    Error: {result['error']}")
    
    print(f"\nISSUES TO FIX:")
    for result in results:
        if result["status"] in ["FAIL", "ERROR"]:
            print(f"  - {result['endpoint']}: {result.get('error', 'Unknown error')}")
    
    return pass_count, fail_count, error_count

def main():
    print("VPVS BACKEND COMPREHENSIVE API TEST")
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = test_api_with_validation()
    pass_count, fail_count, error_count = generate_report(results)
    
    print(f"\nRECOMMENDATIONS:")
    if fail_count > 0 or error_count > 0:
        print("  1. Fix failing endpoints")
        print("  2. Verify deployment status")
        print("  3. Check for syntax errors")
        print("  4. Test with proper data")
    else:
        print("  All endpoints working correctly!")
        print("  Ready for frontend integration testing")

if __name__ == "__main__":
    main()
