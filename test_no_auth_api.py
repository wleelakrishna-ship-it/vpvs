#!/usr/bin/env python3
"""
Test no-auth API endpoints
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def test_endpoint(endpoint, description=""):
    """Test single endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        print(f"  {description}: HTTP {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "error" in data:
                    print(f"    Error in response: {data['error']}")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"    Success: Found {len(data)} items")
                elif isinstance(data, dict):
                    print(f"    Success: {list(data.keys())}")
                else:
                    print(f"    Success: {str(data)[:100]}...")
            except:
                print(f"    Success: {response.text[:100]}...")
        else:
            print(f"    Failed: {response.text[:100]}...")
        return response.status_code
    except Exception as e:
        print(f"  {description}: ERROR - {str(e)}")
        return None

def main():
    print("TESTING NO-AUTH API ENDPOINTS")
    print("="*50)
    
    endpoints = [
        ("/api/health", "Health Check"),
        ("/health", "Root Health"),
        ("/api", "Base API"),
        ("/api/posts", "Posts"),
        ("/api/auth/login", "Login"),
        ("/api/expenses", "Expenses"),
        ("/api/expense-groups", "Expense Groups"),
        ("/api/profiles", "Profiles"),
    ]
    
    results = []
    
    for endpoint, desc in endpoints:
        status = test_endpoint(endpoint, desc)
        results.append((endpoint, status))
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
                test_endpoint(f"/api/posts/{post_id}/comments", "Comments")
                
                # Test likes
                test_endpoint(f"/api/posts/{post_id}/likes", "Likes")
            else:
                print("  No posts available for testing")
        else:
            print("  Could not get posts for testing")
    except Exception as e:
        print(f"  Error getting post ID: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    success_count = len([r for r in results if r[1] and 200 <= r[1] < 300])
    total_count = len([r for r in results if r[1] is not None])
    
    print(f"Total Tests: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Success Rate: {(success_count/total_count*100):.1f}%" if total_count > 0 else "N/A")
    
    print(f"\nWorking Endpoints:")
    for endpoint, status in results:
        if status and 200 <= status < 300:
            print(f"  ✅ {endpoint}")
        elif status:
            print(f"  ❌ {endpoint} (HTTP {status})")
        else:
            print(f"  ❌ {endpoint} (Connection Error)")

if __name__ == "__main__":
    main()
