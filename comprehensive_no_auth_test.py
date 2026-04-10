#!/usr/bin/env python3
"""
Comprehensive test of no-auth API with correct HTTP methods
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test endpoint with correct HTTP method"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}", timeout=10)
        elif method == "HEAD":
            response = requests.head(f"{BASE_URL}{endpoint}", timeout=10)
        
        print(f"  {description}: {method} HTTP {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "error" in data:
                    print(f"    Error in response: {data['error']}")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"    Success: Found {len(data)} items")
                elif isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"    Success: {keys}")
                else:
                    print(f"    Success: {str(data)[:100]}...")
            except:
                print(f"    Success: {response.text[:100]}...")
        else:
            print(f"    Response: {response.text[:100]}...")
        return response.status_code
    except Exception as e:
        print(f"  {description}: ERROR - {str(e)}")
        return None

def main():
    print("COMPREHENSIVE NO-AUTH API TEST")
    print("="*60)
    
    # Test endpoints with correct methods
    endpoints = [
        ("GET", "/api/health", None, "Health Check"),
        ("HEAD", "/api/health", None, "Health Check HEAD"),
        ("GET", "/health", None, "Root Health"),
        ("HEAD", "/health", None, "Root Health HEAD"),
        ("GET", "/api", None, "Base API"),
        ("HEAD", "/api", None, "Base API HEAD"),
        ("GET", "/api/posts", None, "Posts"),
        ("POST", "/api/auth/login", {"username": "testuser", "password": "password123"}, "Login"),
        ("GET", "/api/expenses", None, "Expenses"),
        ("GET", "/api/expense-groups", None, "Expense Groups"),
        ("GET", "/api/profiles", None, "Profiles"),
    ]
    
    results = []
    
    for method, endpoint, data, desc in endpoints:
        status = test_endpoint(method, endpoint, data, desc)
        results.append((endpoint, method, status))
        time.sleep(0.5)
    
    # Test with valid post ID for comments and likes
    print("\nTesting with valid post ID:")
    try:
        # Get a valid post ID
        posts_response = requests.get(f"{BASE_URL}/api/posts", timeout=5)
        if posts_response.status_code == 200:
            posts_data = posts_response.json()
            if posts_data.get("posts") and len(posts_data["posts"]) > 0:
                post_id = posts_data["posts"][0]["id"]
                print(f"  Using post ID: {post_id}")
                
                # Test comments
                status = test_endpoint("GET", f"/api/posts/{post_id}/comments", None, "Comments")
                results.append((f"/api/posts/{post_id}/comments", "GET", status))
                
                # Test likes
                status = test_endpoint("GET", f"/api/posts/{post_id}/likes", None, "Likes")
                results.append((f"/api/posts/{post_id}/likes", "GET", status))
                
                # Test creating a comment
                comment_data = {
                    "post_id": post_id,
                    "username": "testuser",
                    "comment": "Test comment from API test"
                }
                status = test_endpoint("POST", "/api/comments", comment_data, "Create Comment")
                results.append(("/api/comments", "POST", status))
                
                # Test creating a post
                post_data = {
                    "title": "Test Post from API",
                    "description": "This is a test post",
                    "image_url": "https://picsum.photos/seed/test/400/300.jpg"
                }
                status = test_endpoint("POST", "/api/posts", post_data, "Create Post")
                results.append(("/api/posts", "POST", status))
                
            else:
                print("  No posts available for testing")
        else:
            print("  Could not get posts for testing")
    except Exception as e:
        print(f"  Error getting post ID: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*60)
    
    success_count = len([r for r in results if r[2] and 200 <= r[2] < 300])
    total_count = len([r for r in results if r[2] is not None])
    
    print(f"Total Tests: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Success Rate: {(success_count/total_count*100):.1f}%" if total_count > 0 else "N/A")
    
    print(f"\nWorking Endpoints:")
    for endpoint, method, status in results:
        if status and 200 <= status < 300:
            print(f"  {method} {endpoint}")
        elif status:
            print(f"  {method} {endpoint} - HTTP {status}")
        else:
            print(f"  {method} {endpoint} - Connection Error")
    
    # Test specific functionality
    print(f"\nFUNCTIONALITY TESTS:")
    
    # Test signup
    print(f"\nTesting User Signup:")
    signup_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "phone": "9876543210",
        "dob": "2000-01-01",
        "is_admin": False
    }
    test_endpoint("POST", "/api/profiles/signup", signup_data, "User Signup")
    
    # Test expense creation
    print(f"\nTesting Expense Creation:")
    expense_data = {
        "description": "Test Expense",
        "amount": 100.50,
        "type": "expense",
        "date": "2024-01-01"
    }
    test_endpoint("POST", "/api/expenses", expense_data, "Create Expense")
    
    # Test expense group creation
    print(f"\nTesting Expense Group Creation:")
    group_data = {
        "name": "Test Group",
        "description": "Test expense group"
    }
    test_endpoint("POST", "/api/expense-groups", group_data, "Create Expense Group")

if __name__ == "__main__":
    main()
