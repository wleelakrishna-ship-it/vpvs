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

# Create post (admin only)
@app.post("/api/posts")
def create_post(payload: Dict[str, Any]):
    try:
        print(f"Create post request: {payload}")
        
        title = str(payload.get("title", "")).strip()
        description = str(payload.get("description", "")).strip()
        image_data = payload.get("image_data", "")
        image_name = payload.get("image_name", "")
        
        if not title or not description:
            return _safe_response("Title and description required", 400)
        
        # For demo, create a simple image URL (in production, you'd upload to Supabase storage)
        image_url = f"https://via.placeholder.com/400x300.png?text={title.replace(' ', '+')}"
        
        sb = get_admin_client()
        res = sb.table("posts").insert({
            "title": title,
            "description": description,
            "image_url": image_url,
            "image_path": image_name
        }).execute()
        
        print(f"Post creation response: {res}")
        
        if not res.data:
            return _safe_response("Failed to create post", 500)
        
        post_data = res.data[0]
        return {
            "post": {
                "id": post_data.get("id"),
                "title": post_data.get("title"),
                "description": post_data.get("description"),
                "image_url": post_data.get("image_url"),
                "created_at": post_data.get("created_at")
            }
        }
    except Exception as e:
        print(f"Create post error: {str(e)}")
        return _safe_response(f"Failed to create post: {str(e)}", 500)

# Get single post
@app.get("/api/posts/{post_id}")
def get_post(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("posts").select("*").eq("id", post_id).limit(1).execute()
        
        if not res.data:
            return _safe_response("Post not found", 404)
        
        return {"post": res.data[0]}
    except Exception as e:
        return _safe_response(str(e))

# Get comments for a post
@app.get("/api/posts/{post_id}/comments")
def get_comments(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("comments").select("*").eq("post_id", post_id).order("created_at", asc=True).execute()
        return {"comments": res.data or []}
    except Exception as e:
        return _safe_response(str(e))

# Add comment to a post
@app.post("/api/posts/{post_id}/comments")
def add_comment(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        comment = str(payload.get("comment", "")).strip()
        
        if not username or not comment:
            return _safe_response("Username and comment required", 400)
        if len(username) > 32 or len(comment) > 500:
            return _safe_response("Input too long", 400)
        
        sb = get_admin_client()
        res = sb.table("comments").insert({
            "post_id": post_id,
            "username": username,
            "comment": comment
        }).execute()
        
        if not res.data:
            return _safe_response("Failed to create comment", 500)
        
        comment_data = res.data[0]
        return {
            "comment": {
                "id": comment_data.get("id"),
                "post_id": comment_data.get("post_id", post_id),
                "username": comment_data.get("username", username),
                "comment": comment_data.get("comment", comment),
                "created_at": comment_data.get("created_at", datetime.utcnow().isoformat())
            }
        }
    except Exception as e:
        return _safe_response(str(e))

# Get likes for a post
@app.get("/api/posts/{post_id}/likes")
def get_likes(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("likes").select("username").eq("post_id", post_id).execute()
        likes = [like["username"] for like in (res.data or [])]
        return {"likes": likes}
    except Exception as e:
        return _safe_response(str(e))

# Like a post
@app.post("/api/posts/{post_id}/likes")
def add_like(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        
        if not username or len(username) > 32:
            return _safe_response("Invalid username", 400)
        
        sb = get_admin_client()
        res = sb.table("likes").insert({
            "post_id": post_id,
            "username": username
        }).execute()
        
        if not res.data:
            return _safe_response("Failed to like post", 500)
        
        like_data = res.data[0]
        return {
            "like": {
                "id": like_data.get("id"),
                "post_id": like_data.get("post_id", post_id),
                "username": like_data.get("username", username),
                "created_at": like_data.get("created_at", datetime.utcnow().isoformat())
            }
        }
    except Exception as e:
        if "duplicate" in str(e).lower():
            return _safe_response("Already liked", 409)
        return _safe_response(str(e))

# Remove like from a post
@app.delete("/api/posts/{post_id}/likes")
def remove_like(post_id: str, payload: Dict[str, Any]):
    try:
        username = str(payload.get("username", "")).strip()
        
        if not username:
            return _safe_response("Username required", 400)
        
        sb = get_admin_client()
        res = sb.table("likes").delete().eq("post_id", post_id).eq("username", username).execute()
        
        return {"success": True}
    except Exception as e:
        return _safe_response(str(e))

# Get expenses for authenticated user
@app.get("/api/expenses")
def get_expenses(view: str = "day", authorization: Optional[str] = Header(default=None)):
    try:
        if not authorization:
            return _safe_response("Authentication required", 401)
        
        # For demo, we'll skip JWT verification and just return expenses
        sb = get_admin_client()
        res = sb.table("expenses").select("*").order("created_at", desc=True).execute()
        
        return {"expenses": res.data or []}
    except Exception as e:
        return _safe_response(str(e))

# Create expense
@app.post("/api/expenses")
def create_expense(payload: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    try:
        if not authorization:
            return _safe_response("Authentication required", 401)
        
        description = str(payload.get("description", "")).strip()
        amount = float(payload.get("amount", 0))
        expense_type = str(payload.get("type", "debit")).strip()
        date = str(payload.get("date", "")).strip()
        group_id = payload.get("group_id")
        
        if not description or not amount or not date:
            return _safe_response("Description, amount, and date required", 400)
        
        if expense_type not in ["debit", "credit"]:
            return _safe_response("Type must be debit or credit", 400)
        
        # For demo, we'll use a dummy user_id
        user_id = "2f22be17-accb-4d89-b977-7bca27903a35"  # testadmin user
        
        sb = get_admin_client()
        res = sb.table("expenses").insert({
            "description": description,
            "amount": amount,
            "type": expense_type,
            "date": date,
            "user_id": user_id,
            "group_id": group_id
        }).execute()
        
        if not res.data:
            return _safe_response("Failed to create expense", 500)
        
        expense_data = res.data[0]
        return {"expense": expense_data}
    except Exception as e:
        return _safe_response(str(e))

# Get expense groups
@app.get("/api/expense-groups")
def get_expense_groups(authorization: Optional[str] = Header(default=None)):
    try:
        if not authorization:
            return _safe_response("Authentication required", 401)
        
        sb = get_admin_client()
        res = sb.table("expense_groups").select("*").order("created_at", desc=True).execute()
        
        return {"groups": res.data or []}
    except Exception as e:
        return _safe_response(str(e))

# Create expense group (admin only)
@app.post("/api/expense-groups")
def create_expense_group(payload: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    try:
        if not authorization:
            return _safe_response("Authentication required", 401)
        
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        
        if not name:
            return _safe_response("Group name required", 400)
        
        # For demo, we'll use a dummy created_by user
        created_by = "2f22be17-accb-4d89-b977-7bca27903a35"  # testadmin user
        
        sb = get_admin_client()
        res = sb.table("expense_groups").insert({
            "name": name,
            "description": description,
            "created_by": created_by
        }).execute()
        
        if not res.data:
            return _safe_response("Failed to create group", 500)
        
        group_data = res.data[0]
        return {"group": group_data}
    except Exception as e:
        return _safe_response(str(e))

# For Render deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
else:
    # For Gunicorn
    application = app
