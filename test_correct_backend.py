#!/usr/bin/env python3
"""
Test the correct working backend URL
"""

import requests
import json
import time

BASE_URL = "https://vpvs-1.onrender.com"

def log_test(endpoint, method, status_code, response_data=""):
    """Log test result"""
    status_icon = "✅" if status_code == 200 else "❌"
    print(f"{status_icon} {method} {endpoint}")
    print(f"   Status: {status_code}")
    if response_data:
        preview = str(response_data)[:100].replace('\n', ' ')
        print(f"   Response: {preview}...")
    print()

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        log_test("/api/health", "GET", response.status_code, response.text)
    except Exception as e:
        log_test("/api/health", "GET", f"ERROR: {str(e)}")

def test_signup():
    """Test user signup"""
    print("👤 Testing User Signup")
    try:
        user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "phone": "9876543210",
            "dob": "2000-01-01",
            "is_admin": False
        }
        response = requests.post(f"{BASE_URL}/api/profiles/signup", json=user_data, timeout=10)
        log_test("/api/profiles/signup", "POST", response.status_code, response.text)
    except Exception as e:
        log_test("/api/profiles/signup", "POST", f"ERROR: {str(e)}")

def test_login():
    """Test user login"""
    print("🔐 Testing User Login")
    try:
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        log_test("/api/auth/login", "POST", response.status_code, response.text)
    except Exception as e:
        log_test("/api/auth/login", "POST", f"ERROR: {str(e)}")

def test_posts():
    """Test posts endpoints"""
    print("📝 Testing Posts")
    
    # Get all posts
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        data = response.json() if response.status_code == 200 else {}
        post_count = len(data.get('posts', []))
        log_test("/api/posts", "GET", response.status_code, f"Found {post_count} posts")
    except Exception as e:
        log_test("/api/posts", "GET", f"ERROR: {str(e)}")

def test_expenses():
    """Test expenses endpoints"""
    print("💰 Testing Expenses")
    try:
        response = requests.get(f"{BASE_URL}/api/expenses", timeout=10)
        log_test("/api/expenses", "GET", response.status_code, response.text)
    except Exception as e:
        log_test("/api/expenses", "GET", f"ERROR: {str(e)}")

def test_expense_groups():
    """Test expense groups endpoints"""
    print("👥 Testing Expense Groups")
    try:
        response = requests.get(f"{BASE_URL}/api/expense-groups", timeout=10)
        log_test("/api/expense-groups", "GET", response.status_code, response.text)
    except Exception as e:
        log_test("/api/expense-groups", "GET", f"ERROR: {str(e)}")

def test_post_interactions():
    """Test post interaction endpoints"""
    print("💬 Testing Post Interactions")
    
    # Test comments endpoint (GET)
    try:
        response = requests.get(f"{BASE_URL}/api/posts/test-post-id/comments", timeout=10)
        log_test("/api/posts/{id}/comments", "GET", response.status_code, response.text)
    except Exception as e:
        log_test("/api/posts/{id}/comments", "GET", f"ERROR: {str(e)}")
    
    # Test likes endpoint (GET)
    try:
        response = requests.get(f"{BASE_URL}/api/posts/test-post-id/likes", timeout=10)
        log_test("/api/posts/{id}/likes", "GET", response.status_code, response.text)
    except Exception as e:
        log_test("/api/posts/{id}/likes", "GET", f"ERROR: {str(e)}")

def main():
    print("🚀 TESTING CORRECT BACKEND URL")
    print(f"🌐 Target: {BASE_URL}")
    print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all tests
    test_health()
    test_signup()
    test_login()
    test_posts()
    test_expenses()
    test_expense_groups()
    test_post_interactions()
    
    # Summary
    print("="*60)
    print("📊 TEST COMPLETE")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("🎯 Check results above for endpoint status")

if __name__ == "__main__":
    main()
