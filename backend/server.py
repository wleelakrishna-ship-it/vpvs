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
def _safe_error(message: str, status: int = 400):
    raise HTTPException(status_code=status, detail=message)

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
def signup(payload: SignupRequest):
    try:
        # Validate
        if not payload.username or len(payload.username) > 32:
            return _safe_error("Invalid username", 400)
        if not payload.email or "@" not in payload.email:
            return _safe_error("Invalid email", 400)
        if not payload.password or len(payload.password) < 6:
            return _safe_error("Password must be at least 6 characters", 400)
        if not payload.phone or len(payload.phone) != 10 or not payload.phone.isdigit():
            return _safe_error("Phone must be 10 digits", 400)
        if not payload.dob:
            return _safe_error("Date of birth required", 400)

        # Hash password
        hashed_password = sha256(payload.password.encode()).hexdigest()

        # Insert user
        sb = get_admin_client()
        res = sb.table("profiles").insert({
            "username": payload.username,
            "email": payload.email,
            "password": hashed_password,
            "phone": payload.phone,
            "dob": payload.dob,
            "is_admin": payload.is_admin
        }).execute()

        if not res.data:
            return _safe_error("Failed to create user", 500)

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
        if "duplicate" in str(e).lower():
            return _safe_error("Username or email already exists", 409)
        return _safe_error(f"Signup failed: {str(e)}", 500)

# Login
@app.post("/api/auth/login")
def login(payload: LoginRequest):
    try:
        if not payload.username or not payload.password:
            return _safe_error("Username and password required", 400)

        # Hash password
        hashed_password = sha256(payload.password.encode()).hexdigest()

        # Find user
        sb = get_admin_client()
        res = sb.table("profiles").select("*").eq("username", payload.username).limit(1).execute()

        if not res.data:
            return _safe_error("Invalid credentials", 401)

        user = res.data[0]
        
        # Verify password
        if user.get("password") != hashed_password:
            return _safe_error("Invalid credentials", 401)

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
        return _safe_error(f"Login failed: {str(e)}", 500)

# Get posts (existing functionality)
@app.get("/api/posts")
def get_posts():
    try:
        sb = get_admin_client()
        res = sb.table("posts").select("id,title,description,image_url,created_at").order("created_at", desc=True).execute()
        return {"posts": res.data or []}
    except Exception as e:
        return _safe_error(str(e))

# For Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
else:
    # For Gunicorn
    application = app
