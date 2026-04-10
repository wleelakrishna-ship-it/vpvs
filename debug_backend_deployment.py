#!/usr/bin/env python3
"""
Debug backend deployment issues
"""

import requests
import time

def test_render_endpoints():
    """Test various endpoint patterns to find working routes"""
    base_urls = [
        "https://vpvs-backend.onrender.com",
        "https://vpvs-1.onrender.com", 
        "https://vpvs.onrender.com"
    ]
    
    endpoints_to_test = [
        "/",
        "/health",
        "/api/health", 
        "/api",
        "/api/posts",
        "/api/auth/login",
        "/docs",
        "/openapi.json"
    ]
    
    print("🔍 TESTING MULTIPLE RENDER URLS AND ENDPOINTS")
    print("="*60)
    
    for base_url in base_urls:
        print(f"\n🌐 Testing: {base_url}")
        print("-" * 40)
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"  {status} {endpoint}")
                
                if response.status_code == 200 and len(response.text) > 0:
                    content_preview = response.text[:100].replace('\n', ' ')
                    print(f"     Content: {content_preview}...")
                    
            except requests.exceptions.Timeout:
                print(f"  ⏰ {endpoint} - TIMEOUT")
            except requests.exceptions.ConnectionError:
                print(f"  🔌 {endpoint} - CONNECTION ERROR")
            except Exception as e:
                print(f"  ❌ {endpoint} - ERROR: {str(e)[:50]}")
        
        time.sleep(1)  # Rate limiting

def test_frontend_url_mapping():
    """Test frontend URL mapping to backend"""
    print(f"\n🎨 TESTING FRONTEND URL MAPPING")
    print("="*60)
    
    frontend_urls = [
        "https://vpvs-p8q4-bn2wkea6f-vpvs.vercel.app",
        "https://vpvs.netlify.app"
    ]
    
    backend_urls = [
        "https://vpvs-backend.onrender.com",
        "https://vpvs-1.onrender.com"
    ]
    
    for frontend in frontend_urls:
        print(f"\n🎨 Frontend: {frontend}")
        for backend in backend_urls:
            try:
                # Test if frontend can reach backend
                test_url = f"{frontend}/api/health"
                response = requests.get(test_url, timeout=5, allow_redirects=True)
                final_url = response.url if response.url else test_url
                status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"  → {backend}: {status}")
                if response.status_code != 200 and "render" in final_url:
                    print(f"    Redirected to: {final_url}")
            except Exception as e:
                print(f"  → {backend}: ❌ ERROR: {str(e)[:30]}")

def check_render_service_status():
    """Check Render service status"""
    print(f"\n🔧 CHECKING RENDER SERVICE STATUS")
    print("="*60)
    
    try:
        # Check if Render service is responding
        response = requests.get("https://status.render.com/", timeout=10)
        print(f"✅ Render Status Page: {response.status_code}")
        
        # Check specific service
        service_urls = [
            "https://vpvs-backend.onrender.com/health",
            "https://vpvs-1.onrender.com/health"
        ]
        
        for service_url in service_urls:
            try:
                response = requests.get(service_url, timeout=5)
                domain = service_url.split('//')[1].split('/')[0]
                status = "✅ UP" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"  {domain}: {status}")
            except:
                domain = service_url.split('//')[1].split('/')[0]
                print(f"  {domain}: ❌ DOWN")
                
    except Exception as e:
        print(f"❌ Render Status Check Failed: {e}")

def main():
    print("🚀 BACKEND DEPLOYMENT DEBUG")
    print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_render_service_status()
    test_render_endpoints()
    test_frontend_url_mapping()
    
    print(f"\n📊 SUMMARY")
    print("="*60)
    print("🔍 Check which Render URL is actually working")
    print("🎨 Verify frontend can reach backend")
    print("🔧 Look for deployment configuration issues")
    print("\n📞 NEXT STEPS:")
    print("1. Identify correct Render URL")
    print("2. Update frontend environment if needed")
    print("3. Fix any routing issues")
    print("4. Test all API endpoints")

if __name__ == "__main__":
    main()
