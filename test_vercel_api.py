import requests
import json
import time

# Vercel API base URL
base_url = "https://vpvs-p8q4.vercel.app"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test API endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
        else:
            return False, f"Unsupported method: {method}"
        
        print(f"\n{'='*50}")
        print(f"TEST: {method} {endpoint}")
        print(f"STATUS: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"RESPONSE: {json.dumps(response_data, indent=2)}")
        except:
            print(f"RAW RESPONSE: {response.text}")
        
        return response.status_code == 200, response.status_code
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False, str(e)

def main():
    print("🧪 TESTING VPVS VERCEL API")
    print("=" * 60)
    
    results = []
    
    # 1. Health Check
    print("\n1️⃣ HEALTH CHECK")
    success, status = test_endpoint("GET", "/")
    results.append(("Health Check", success, status))
    
    # 2. API Health Check
    print("\n2️⃣ API HEALTH CHECK")
    success, status = test_endpoint("GET", "/api")
    results.append(("API Health Check", success, status))
    
    # 3. Get Posts
    print("\n3️⃣ GET POSTS")
    success, status = test_endpoint("GET", "/api/posts")
    results.append(("Get Posts", success, status))
    
    # 4. Signup Test
    print("\n4️⃣ SIGNUP TEST")
    signup_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@test.com",
        "password": "password123",
        "phone": "1234567890",
        "dob": "2000-01-01",
        "is_admin": False
    }
    success, status = test_endpoint("POST", "/api/profiles/signup", signup_data)
    results.append(("Signup", success, status))
    
    # 5. Login Test (with existing user)
    print("\n5️⃣ LOGIN TEST")
    login_data = {
        "username": "testadmin",
        "password": "password123"
    }
    success, status = test_endpoint("POST", "/api/auth/login", login_data)
    results.append(("Login", success, status))
    
    # 6. Create Post Test
    print("\n6️⃣ CREATE POST TEST")
    post_data = {
        "title": f"Test Post {int(time.time())}",
        "description": "This is a test post created via API testing",
        "image_url": "https://via.placeholder.com/400x300.png?text=Test"
    }
    success, status = test_endpoint("POST", "/api/posts", post_data)
    results.append(("Create Post", success, status))
    
    # 7. Get Expenses
    print("\n7️⃣ GET EXPENSES")
    success, status = test_endpoint("GET", "/api/expenses")
    results.append(("Get Expenses", success, status))
    
    # 8. Create Expense Test
    print("\n8️⃣ CREATE EXPENSE TEST")
    expense_data = {
        "description": f"Test Expense {int(time.time())}",
        "amount": "100.50",
        "type": "debit",
        "date": "2024-01-01"
    }
    success, status = test_endpoint("POST", "/api/expenses", expense_data)
    results.append(("Create Expense", success, status))
    
    # 9. Get Expense Groups
    print("\n9️⃣ GET EXPENSE GROUPS")
    success, status = test_endpoint("GET", "/api/expense-groups")
    results.append(("Get Expense Groups", success, status))
    
    # 10. Create Expense Group Test
    print("\n🔟 CREATE EXPENSE GROUP TEST")
    group_data = {
        "name": f"Test Group {int(time.time())}",
        "description": "This is a test expense group"
    }
    success, status = test_endpoint("POST", "/api/expense-groups", group_data)
    results.append(("Create Expense Group", success, status))
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success, status in results:
        if success:
            print(f"✅ {test_name}: PASS ({status})")
            passed += 1
        else:
            print(f"❌ {test_name}: FAIL ({status})")
            failed += 1
    
    print(f"\n📈 TOTAL: {passed + failed} tests")
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! API is working correctly!")
    else:
        print(f"\n⚠️ {failed} tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    main()
