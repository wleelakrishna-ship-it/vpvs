import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from hashlib import sha256

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

# FastAPI app
app = FastAPI(title="VPVS API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment helpers
def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        # For testing, provide fallback values
        if key == "SUPABASE_URL":
            return "https://eaufubpzxbgfqtutjalo.supabase.co"
        elif key == "SUPABASE_ANON_KEY":
            return "sb_publishable_51j7QV7dhTacsOpJkfVceA_oFU31WPJ"
        elif key == "SUPABASE_SERVICE_ROLE_KEY":
            return "sb_secret_NeuEJonW2p8YGGyv1551Yg_Ge-BHrXH"
        elif key == "SUPABASE_STORAGE_BUCKET":
            return "images"
        raise HTTPException(status_code=500, detail=f"Missing env: {key}")
    return val

# Supabase clients
def get_admin_client() -> Client:
    return create_client(
        get_env("SUPABASE_URL"),
        get_env("SUPABASE_SERVICE_ROLE_KEY")
    )

def get_anon_client() -> Client:
    return create_client(
        get_env("SUPABASE_URL"),
        get_env("SUPABASE_ANON_KEY")
    )

# Error helper
def _safe_response(message: str, status: int = 400):
    return {"error": message}, status

# Models
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: str
    dob: str
    is_admin: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str

# Health check
@app.get("/")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Health check with api prefix
@app.get("/api")
def health_api():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Signup
@app.post("/api/profiles/signup")
def signup(payload: Dict[str, Any]):
    try:
        print(f"Signup request received: {payload}")
        
        # Validate
        username = str(payload.get("username", "")).strip()
        email = str(payload.get("email", "")).strip()
        password = str(payload.get("password", "")).strip()
        phone = str(payload.get("phone", "")).strip()
        dob = str(payload.get("dob", "")).strip()
        is_admin = bool(payload.get("is_admin", False))
        
        if not username or len(username) > 32:
            return _safe_response("Invalid username", 400)
        if not email or "@" not in email:
            return _safe_response("Invalid email", 400)
        if not password or len(password) < 6:
            return _safe_response("Password must be at least 6 characters", 400)
        if not phone or len(phone) != 10 or not phone.isdigit():
            return _safe_response("Phone must be 10 digits", 400)
        if not dob:
            return _safe_response("Date of birth required", 400)

        print("Validation passed, attempting to create user...")
        
        # Hash password
        hashed_password = sha256(password.encode()).hexdigest()
        print(f"Password hashed: {hashed_password[:10]}...")

        # Insert user
        sb = get_admin_client()
        res = sb.table("profiles").insert({
            "username": username,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "dob": dob,
            "is_admin": is_admin
        }).execute()

        print(f"Supabase response: {res}")

        if not res.data:
            return _safe_response("Failed to create user", 500)

        user_data = res.data[0]
        return {
            "profile": {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "is_admin": user_data.get("is_admin"),
                "created_at": user_data.get("created_at")
            }
        }
    except Exception as e:
        print(f"Signup error: {str(e)}")
        if "duplicate" in str(e).lower():
            return _safe_response("Username or email already exists", 409)
        return _safe_response(f"Signup failed: {str(e)}", 500)

# Login
@app.post("/api/auth/login")
def login(payload: Dict[str, Any]):
    try:
        print(f"Login request received: {payload.get('username')}")
        
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()
        
        if not username or not password:
            return _safe_response("Username and password required", 400)

        # Hash password
        hashed_password = sha256(password.encode()).hexdigest()
        print(f"Login password hashed: {hashed_password[:10]}...")

        # Find user
        sb = get_admin_client()
        res = sb.table("profiles").select("*").eq("username", username).limit(1).execute()

        print(f"User lookup response: {res}")

        if not res.data:
            return _safe_response("Invalid credentials", 401)

        user = res.data[0]
        print(f"Found user: {user.get('username')}")
        
        # Verify password
        stored_password = user.get("password")
        print(f"Stored password: {stored_password[:10] if stored_password else 'None'}...")
        
        if stored_password != hashed_password:
            return _safe_response("Invalid credentials", 401)

        # Create simple token (for demo)
        token = str(uuid.uuid4())

        return {
            "user": {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False)
            },
            "token": token
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        return _safe_response(f"Login failed: {str(e)}", 500)

# Get posts (existing functionality)
@app.get("/api/posts")
def get_posts():
    try:
        sb = get_admin_client()
        res = sb.table("posts").select("id,title,description,image_url,created_at").order("created_at", desc=True).execute()
        return {"posts": res.data or []}
    except Exception as e:
        return _safe_response(str(e))

# For Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
else:
    # For Gunicorn
    application = app
