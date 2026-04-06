#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all VPVS backend endpoints on production
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://vpvs-backend.onrender.com"
TEST_RESULTS = []

# Test users data
ADMIN_USER = {
    "username": f"admin_test_{int(time.time())}",
    "email": f"admin_test_{int(time.time())}@example.com",
    "password": "password123",
    "phone": "9876543210",
    "dob": "2000-01-01",
    "is_admin": True
}

REGULAR_USER = {
    "username": f"user_test_{int(time.time())}",
    "email": f"user_test_{int(time.time())}@example.com", 
    "password": "password123",
    "phone": "9876543211",
    "dob": "2000-01-01",
    "is_admin": False
}

def log_test(endpoint, method, status, expected, actual, details=""):
    """Log test results"""
    result = {
        "endpoint": endpoint,
        "method": method,
        "expected": expected,
        "actual": actual,
        "status": "PASS" if expected == actual else "FAIL",
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    
    status_icon = "✅" if result["status"] == "PASS" else "❌"
    print(f"{status_icon} {method} {endpoint}")
    print(f"   Expected: {expected}, Got: {actual}")
    if details:
        print(f"   Details: {details}")
    print()

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        log_test("/api/health", "GET", 200, response.status_code, response.json())
    except Exception as e:
        log_test("/api/health", "GET", 200, f"ERROR: {str(e)}", str(e))

def test_user_signup():
    """Test user signup endpoints"""
    print("👤 Testing User Signup")
    
    # Test admin signup
    try:
        response = requests.post(f"{BASE_URL}/api/profiles/signup", 
                           json=ADMIN_USER, timeout=10)
        if response.status_code == 201:
            ADMIN_USER.update(response.json().get("profile", {}))
            log_test("/api/profiles/signup", "POST", 201, response.status_code, "Admin signup successful")
        else:
            log_test("/api/profiles/signup", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/profiles/signup", "POST", 201, f"ERROR: {str(e)}", str(e))
    
    # Test regular user signup
    try:
        response = requests.post(f"{BASE_URL}/api/profiles/signup", 
                           json=REGULAR_USER, timeout=10)
        if response.status_code == 201:
            REGULAR_USER.update(response.json().get("profile", {}))
            log_test("/api/profiles/signup", "POST", 201, response.status_code, "Regular user signup successful")
        else:
            log_test("/api/profiles/signup", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/profiles/signup", "POST", 201, f"ERROR: {str(e)}", str(e))

def test_user_login():
    """Test user login endpoints"""
    print("🔐 Testing User Login")
    
    # Test admin login
    try:
        login_data = {
            "username": ADMIN_USER["username"],
            "password": ADMIN_USER["password"]
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json=login_data, timeout=10)
        if response.status_code == 200:
            admin_token = response.json().get("token")
            ADMIN_USER["token"] = admin_token
            log_test("/api/auth/login", "POST", 200, response.status_code, "Admin login successful")
        else:
            log_test("/api/auth/login", "POST", 200, response.status_code, response.text)
    except Exception as e:
        log_test("/api/auth/login", "POST", 200, f"ERROR: {str(e)}", str(e))
    
    # Test regular user login
    try:
        login_data = {
            "username": REGULAR_USER["username"],
            "password": REGULAR_USER["password"]
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                           json=login_data, timeout=10)
        if response.status_code == 200:
            user_token = response.json().get("token")
            REGULAR_USER["token"] = user_token
            log_test("/api/auth/login", "POST", 200, response.status_code, "Regular user login successful")
        else:
            log_test("/api/auth/login", "POST", 200, response.status_code, response.text)
    except Exception as e:
        log_test("/api/auth/login", "POST", 200, f"ERROR: {str(e)}", str(e))

def test_posts():
    """Test posts endpoints"""
    print("📝 Testing Posts")
    
    # Get all posts
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        log_test("/api/posts", "GET", 200, response.status_code, f"Found {len(response.json().get('posts', []))} posts")
    except Exception as e:
        log_test("/api/posts", "GET", 200, f"ERROR: {str(e)}", str(e))
    
    # Create post (admin only)
    if "token" in ADMIN_USER:
        try:
            post_data = {
                "title": "Test Post from API Test",
                "description": "This is a test post created during API testing",
                "image_url": "https://via.placeholder.com/300x200.png"
            }
            headers = {"Authorization": f"Bearer {ADMIN_USER['token']}"}
            response = requests.post(f"{BASE_URL}/api/posts", 
                                json=post_data, headers=headers, timeout=10)
            if response.status_code == 200 or response.status_code == 201:
                post_id = response.json().get("post", {}).get("id")
                ADMIN_USER["test_post_id"] = post_id
                log_test("/api/posts", "POST", 201, response.status_code, "Admin post creation successful")
            else:
                log_test("/api/posts", "POST", 201, response.status_code, response.text)
        except Exception as e:
            log_test("/api/posts", "POST", 201, f"ERROR: {str(e)}", str(e))

def test_comments():
    """Test comments endpoints"""
    print("💬 Testing Comments")
    
    if "test_post_id" not in ADMIN_USER:
        log_test("/api/posts/{id}/comments", "POST", 201, "SKIPPED", "No test post available")
        return
    
    post_id = ADMIN_USER["test_post_id"]
    
    # Add comment
    try:
        comment_data = {
            "comment": "This is a test comment from API testing",
            "username": REGULAR_USER["username"]
        }
        headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
        response = requests.post(f"{BASE_URL}/api/posts/{post_id}/comments", 
                            json=comment_data, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 201:
            comment_id = response.json().get("comment", {}).get("id")
            ADMIN_USER["test_comment_id"] = comment_id
            log_test("/api/posts/{id}/comments", "POST", 201, response.status_code, "Comment creation successful")
        else:
            log_test("/api/posts/{id}/comments", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/posts/{id}/comments", "POST", 201, f"ERROR: {str(e)}", str(e))
    
    # Get comments
    try:
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}/comments", timeout=10)
        log_test("/api/posts/{id}/comments", "GET", 200, response.status_code, 
                 f"Found {len(response.json().get('comments', []))} comments")
    except Exception as e:
        log_test("/api/posts/{id}/comments", "GET", 200, f"ERROR: {str(e)}", str(e))

def test_likes():
    """Test likes endpoints"""
    print("❤️ Testing Likes")
    
    if "test_post_id" not in ADMIN_USER:
        log_test("/api/posts/{id}/like", "POST", 200, "SKIPPED", "No test post available")
        return
    
    post_id = ADMIN_USER["test_post_id"]
    
    # Like post
    try:
        headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
        response = requests.post(f"{BASE_URL}/api/posts/{post_id}/like", 
                            headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 201:
            log_test("/api/posts/{id}/like", "POST", 201, response.status_code, "Like successful")
        else:
            log_test("/api/posts/{id}/like", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/posts/{id}/like", "POST", 201, f"ERROR: {str(e)}", str(e))
    
    # Get likes
    try:
        response = requests.get(f"{BASE_URL}/api/posts/{post_id}/likes", timeout=10)
        log_test("/api/posts/{id}/likes", "GET", 200, response.status_code, 
                 f"Found {len(response.json().get('likes', []))} likes")
    except Exception as e:
        log_test("/api/posts/{id}/likes", "GET", 200, f"ERROR: {str(e)}", str(e))
    
    # Unlike post
    try:
        headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
        response = requests.post(f"{BASE_URL}/api/posts/{post_id}/unlike", 
                            headers=headers, timeout=10)
        if response.status_code == 200:
            log_test("/api/posts/{id}/unlike", "POST", 200, response.status_code, "Unlike successful")
        else:
            log_test("/api/posts/{id}/unlike", "POST", 200, response.status_code, response.text)
    except Exception as e:
        log_test("/api/posts/{id}/unlike", "POST", 200, f"ERROR: {str(e)}", str(e))

def test_expenses():
    """Test expenses endpoints"""
    print("💰 Testing Expenses")
    
    # Create expense
    try:
        expense_data = {
            "description": "Test Expense from API Test",
            "amount": 100.50,
            "type": "debit",
            "date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
        response = requests.post(f"{BASE_URL}/api/expenses", 
                            json=expense_data, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 201:
            expense_id = response.json().get("expense", {}).get("id")
            REGULAR_USER["test_expense_id"] = expense_id
            log_test("/api/expenses", "POST", 201, response.status_code, "Expense creation successful")
        else:
            log_test("/api/expenses", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/expenses", "POST", 201, f"ERROR: {str(e)}", str(e))
    
    # Get expenses
    try:
        headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
        response = requests.get(f"{BASE_URL}/api/expenses", headers=headers, timeout=10)
        log_test("/api/expenses", "GET", 200, response.status_code, 
                 f"Found {len(response.json().get('expenses', []))} expenses")
    except Exception as e:
        log_test("/api/expenses", "GET", 200, f"ERROR: {str(e)}", str(e))
    
    # Update expense
    if "test_expense_id" in REGULAR_USER:
        try:
            update_data = {
                "description": "Updated Test Expense",
                "amount": 150.75,
                "type": "credit",
                "date": "2024-01-02"
            }
            headers = {"Authorization": f"Bearer {REGULAR_USER['token']}"}
            response = requests.put(f"{BASE_URL}/api/expenses/{REGULAR_USER['test_expense_id']}", 
                               json=update_data, headers=headers, timeout=10)
            if response.status_code == 200:
                log_test("/api/expenses/{id}", "PUT", 200, response.status_code, "Expense update successful")
            else:
                log_test("/api/expenses/{id}", "PUT", 200, response.status_code, response.text)
        except Exception as e:
            log_test("/api/expenses/{id}", "PUT", 200, f"ERROR: {str(e)}", str(e))

def test_expense_groups():
    """Test expense groups endpoints"""
    print("👥 Testing Expense Groups")
    
    # Create expense group (admin only)
    try:
        group_data = {
            "name": "Test Group from API Test",
            "description": "This is a test expense group created during API testing"
        }
        headers = {"Authorization": f"Bearer {ADMIN_USER['token']}"}
        response = requests.post(f"{BASE_URL}/api/expense-groups", 
                            json=group_data, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 201:
            group_id = response.json().get("group", {}).get("id")
            ADMIN_USER["test_group_id"] = group_id
            log_test("/api/expense-groups", "POST", 201, response.status_code, "Admin group creation successful")
        else:
            log_test("/api/expense-groups", "POST", 201, response.status_code, response.text)
    except Exception as e:
        log_test("/api/expense-groups", "POST", 201, f"ERROR: {str(e)}", str(e))
    
    # Get expense groups
    try:
        headers = {"Authorization": f"Bearer {ADMIN_USER['token']}"}
        response = requests.get(f"{BASE_URL}/api/expense-groups", headers=headers, timeout=10)
        log_test("/api/expense-groups", "GET", 200, response.status_code, 
                 f"Found {len(response.json().get('groups', []))} groups")
    except Exception as e:
        log_test("/api/expense-groups", "GET", 200, f"ERROR: {str(e)}", str(e))

def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE BACKEND TEST REPORT")
    print("="*80)
    
    passed = len([r for r in TEST_RESULTS if r["status"] == "PASS"])
    failed = len([r for r in TEST_RESULTS if r["status"] == "FAIL"])
    total = len(TEST_RESULTS)
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
    
    if failed > 0:
        print(f"\n❌ FAILED TESTS:")
        for result in TEST_RESULTS:
            if result["status"] == "FAIL":
                print(f"   • {result['method']} {result['endpoint']}")
                print(f"     Expected: {result['expected']}, Got: {result['actual']}")
                if result["details"]:
                    print(f"     Details: {result['details']}")
    
    print(f"\n🔧 TEST USERS CREATED:")
    print(f"   Admin User: {ADMIN_USER.get('username', 'N/A')}")
    print(f"   Regular User: {REGULAR_USER.get('username', 'N/A')}")
    
    print(f"\n🌐 BASE URL: {BASE_URL}")
    print("="*80)

def main():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE BACKEND API TESTING")
    print(f"🌐 Target: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    print("="*80)
    
    # Run all tests in sequence
    test_health_check()
    test_user_signup()
    test_user_login()
    test_posts()
    test_comments()
    test_likes()
    test_expenses()
    test_expense_groups()
    
    # Generate final report
    generate_report()

if __name__ == "__main__":
    main()
