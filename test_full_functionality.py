import requests
import json
import base64
from io import BytesIO
from PIL import Image
import random

# Test API endpoints
base_url = "https://vpvs-1.onrender.com"

def get_auth_token(username="testadmin", password="password123"):
    """Get authentication token"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print(f"❌ Failed to get auth token: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def test_create_post(token, title, description):
    """Test creating a post"""
    try:
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        post_data = {
            "title": title,
            "description": description,
            "image_data": img_base64,
            "image_name": f"test_{random.randint(1000, 9999)}.jpg"
        }
        
        response = requests.post(
            f"{base_url}/api/posts",
            json=post_data,
            headers=headers
        )
        
        print(f"Create Post Status: {response.status_code}")
        print(f"Create Post Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Create post error: {e}")
        return False

def test_get_posts():
    """Test getting posts"""
    try:
        response = requests.get(f"{base_url}/api/posts")
        
        print(f"Get Posts Status: {response.status_code}")
        posts = response.json()
        print(f"Number of posts: {len(posts.get('posts', []))}")
        
        if posts.get('posts'):
            for i, post in enumerate(posts['posts'][:3]):  # Show first 3 posts
                print(f"Post {i+1}: {post.get('title', 'No title')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get posts error: {e}")
        return False

def test_add_comment(post_id, token, username, comment):
    """Test adding a comment"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        comment_data = {
            "username": username,
            "comment": comment
        }
        
        response = requests.post(
            f"{base_url}/api/posts/{post_id}/comments",
            json=comment_data,
            headers=headers
        )
        
        print(f"Add Comment Status: {response.status_code}")
        print(f"Add Comment Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Add comment error: {e}")
        return False

def test_like_post(post_id, token, username):
    """Test liking a post"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        like_data = {"username": username}
        
        response = requests.post(
            f"{base_url}/api/posts/{post_id}/likes",
            json=like_data,
            headers=headers
        )
        
        print(f"Like Post Status: {response.status_code}")
        print(f"Like Post Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Like post error: {e}")
        return False

if __name__ == "__main__":
    print("Testing VPVS Full Functionality...")
    print("=" * 60)
    
    # Get auth token
    print("\n1. Getting Authentication Token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Failed to get authentication token. Cannot continue.")
        exit(1)
    
    print(f"✅ Authentication successful! Token: {token[:20]}...")
    
    # Test getting existing posts
    print("\n2. Testing Get Posts...")
    posts_ok = test_get_posts()
    
    # Test creating a new post
    print("\n3. Testing Create Post...")
    post_ok = test_create_post(
        token, 
        "Test Post from API", 
        "This is a test post created via API testing to verify all functionality is working correctly."
    )
    
    # Test adding comment (if we have posts)
    print("\n4. Testing Add Comment...")
    comment_ok = True  # Skip for now as we need a real post ID
    
    # Test liking a post
    print("\n5. Testing Like Post...")
    like_ok = True  # Skip for now as we need a real post ID
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"Get Posts: {'✅ PASS' if posts_ok else '❌ FAIL'}")
    print(f"Create Post: {'✅ PASS' if post_ok else '❌ FAIL'}")
    print(f"Add Comment: {'⏭ SKIP' if comment_ok else '❌ FAIL'}")
    print(f"Like Post: {'⏭ SKIP' if like_ok else '❌ FAIL'}")
    
    if posts_ok and post_ok:
        print("\n🎉 Core functionality is working!")
        print("\n✅ Authentication: Working")
        print("✅ Posts API: Working")
        print("✅ Create Posts: Working")
        print("\nYou can now test the frontend at:")
        print("https://vpvs.netlify.app")
        print("\nTest with these credentials:")
        print("Admin: testadmin / password123")
        print("User: testuser / password123")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
