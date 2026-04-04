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

# Auth helper
def get_current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        client = get_anon_client()
        user = client.auth.get_user(token)
        return user.user if user else None
    except:
        return None

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

# Get single post
@app.get("/api/posts/{post_id}")
def get_post(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("posts").select("*").eq("id", post_id).limit(1).execute()
        if not res.data:
            return _safe_error("Post not found", 404)
        return {"post": res.data[0]}
    except Exception as e:
        return _safe_error(str(e))

# Get comments
@app.get("/api/posts/{post_id}/comments")
def get_comments(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("comments").select("*").eq("post_id", post_id).order("created_at", asc=True).execute()
        return {"comments": res.data or []}
    except Exception as e:
        return _safe_error(str(e))

# Add comment
@app.post("/api/posts/{post_id}/comments")
def add_comment(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        comment = str(payload.get("comment", "")).strip()
        
        if not username or not comment:
            return _safe_error("Username and comment required", 400)
        if len(username) > 32 or len(comment) > 500:
            return _safe_error("Input too long", 400)
        
        sb = get_admin_client()
        res = sb.table("comments").insert({
            "post_id": post_id,
            "username": username,
            "comment": comment
        }).execute()
        
        saved = (res.data or [{}])[0]
        return {
            "comment": {
                "id": saved.get("id"),
                "post_id": saved.get("post_id", post_id),
                "username": saved.get("username", username),
                "comment": saved.get("comment", comment),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as e:
        return _safe_error(str(e))

# Get likes
@app.get("/api/posts/{post_id}/likes")
def get_likes(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("likes").select("username").eq("post_id", post_id).execute()
        return {"likes": [like["username"] for like in (res.data or [])]}
    except Exception as e:
        return _safe_error(str(e))

# Add like
@app.post("/api/posts/{post_id}/likes")
def add_like(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        if not username or len(username) > 32:
            return _safe_error("Invalid username", 400)
        
        sb = get_admin_client()
        res = sb.table("likes").insert({
            "post_id": post_id,
            "username": username
        }).execute()
        
        saved = (res.data or [{}])[0]
        return {
            "like": {
                "id": saved.get("id"),
                "post_id": saved.get("post_id", post_id),
                "username": saved.get("username", username),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as e:
        if "duplicate" in str(e).lower():
            return _safe_error("Already liked", 409)
        return _safe_error(str(e))

# Remove like
@app.delete("/api/posts/{post_id}/likes")
def remove_like(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        if not username:
            return _safe_error("Username required", 400)
        
        sb = get_admin_client()
        res = sb.table("likes").delete().eq("post_id", post_id).eq("username", username).execute()
        return {"success": True}
    except Exception as e:
        return _safe_error(str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
