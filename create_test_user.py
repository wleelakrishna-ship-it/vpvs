from supabase import create_client
from hashlib import sha256
import os

# Supabase configuration
SUPABASE_URL = "https://eaufubpzxbgfqtutjalo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "sb_secret_NeuEJonW2p8YGGyv1551Yg_Ge-BHrXH"

# Create Supabase client
sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def create_test_admin():
    """Create a test admin user"""
    try:
        # Hash password
        password = "password123"
        hashed_password = sha256(password.encode()).hexdigest()
        
        # Create admin user
        user_data = {
            "username": "testadmin",
            "email": "testadmin@test.com",
            "password": hashed_password,
            "phone": "1234567890",
            "dob": "2000-01-01",
            "is_admin": True
        }
        
        print("Creating test admin user...")
        result = sb.table("profiles").insert(user_data).execute()
        
        if result.data:
            print(f"✅ Test admin created successfully!")
            print(f"User ID: {result.data[0]['id']}")
            print(f"Username: testadmin")
            print(f"Password: password123")
            print(f"Email: testadmin@test.com")
            return True
        else:
            print(f"❌ Failed to create admin: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return False

def create_test_user():
    """Create a test regular user"""
    try:
        # Hash password
        password = "password123"
        hashed_password = sha256(password.encode()).hexdigest()
        
        # Create regular user
        user_data = {
            "username": "testuser",
            "email": "testuser@test.com",
            "password": hashed_password,
            "phone": "1234567890",
            "dob": "2000-01-01",
            "is_admin": False
        }
        
        print("Creating test regular user...")
        result = sb.table("profiles").insert(user_data).execute()
        
        if result.data:
            print(f"✅ Test user created successfully!")
            print(f"User ID: {result.data[0]['id']}")
            print(f"Username: testuser")
            print(f"Password: password123")
            print(f"Email: testuser@test.com")
            return True
        else:
            print(f"❌ Failed to create user: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

if __name__ == "__main__":
    print("Creating test users in Supabase...")
    print("=" * 50)
    
    # Create test admin
    admin_success = create_test_admin()
    
    print("\n" + "=" * 50)
    
    # Create test regular user
    user_success = create_test_user()
    
    print("\n" + "=" * 50)
    if admin_success and user_success:
        print("🎉 Both test users created successfully!")
        print("\nYou can now test login with:")
        print("Admin: testadmin / password123")
        print("User: testuser / password123")
    else:
        print("⚠️ Some users failed to create. Check errors above.")
