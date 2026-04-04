import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from hashlib import sha256

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# Mock user store (for testing without database)
users_db = {}

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

        # Check if user exists
        if payload.username in users_db or any(u['email'] == payload.email for u in users_db.values()):
            return _safe_error("Username or email already exists", 409)

        # Hash password
        hashed_password = sha256(payload.password.encode()).hexdigest()

        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": payload.username,
            "email": payload.email,
            "password": hashed_password,
            "phone": payload.phone,
            "dob": payload.dob,
            "is_admin": payload.is_admin,
            "created_at": datetime.utcnow().isoformat()
        }
        
        users_db[user_id] = user_data

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
        user = None
        for u in users_db.values():
            if u.get("username") == payload.username:
                user = u
                break

        if not user:
            return _safe_error("Invalid credentials", 401)

        # Verify password
        if user.get("password") != hashed_password:
            return _safe_error("Invalid credentials", 401)

        # Create simple token
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
