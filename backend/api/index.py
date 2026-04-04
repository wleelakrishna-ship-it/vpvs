import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
from dotenv import load_dotenv

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import Client, create_client

load_dotenv()

app = FastAPI(title="VPVS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val


def get_admin_client() -> Client:
    return create_client(_env("SUPABASE_URL"), _env("SUPABASE_SERVICE_ROLE_KEY"))


def get_anon_client() -> Client:
    return create_client(_env("SUPABASE_URL"), _env("SUPABASE_ANON_KEY"))


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1]:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return parts[1]


def require_admin(authorization: Optional[str]) -> Dict[str, Any]:
    token = _extract_token(authorization)
    client = get_anon_client()
    user_resp = client.auth.get_user(token)
    user = getattr(user_resp, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    app_metadata = getattr(user, "app_metadata", {}) or {}
    user_metadata = getattr(user, "user_metadata", {}) or {}
    role = app_metadata.get("role") or user_metadata.get("role")
    roles = app_metadata.get("roles") if isinstance(app_metadata.get("roles"), list) else []
    is_admin = role == "admin" or "admin" in roles
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    return {"id": getattr(user, "id", None), "token": token}


def get_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    if not authorization:
        return None
    try:
        token = _extract_token(authorization)
        client = get_anon_client()
        user_resp = client.auth.get_user(token)
        user = getattr(user_resp, "user", None)
        if not user:
            return None
        return {"id": getattr(user, "id", None), "token": token}
    except:
        return None


def _safe_error(message: str, status_code: int = 500) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"ok": "true"}


@app.get("/api/posts")
def get_posts():
    try:
        sb = get_admin_client()
        res = (
            sb.table("posts")
            .select("id,title,description,image_url,created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return {"posts": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/posts/{post_id}")
def get_post_by_id(post_id: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("posts")
            .select("id,title,description,image_url,created_at")
            .eq("id", post_id)
            .limit(1)
            .execute()
        )
        if not res.data:
            return _safe_error("Post not found", 404)
        return {"post": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/posts")
async def create_post(
    title: str = Form(...),
    description: str = Form(""),
    image: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
):
    try:
        require_admin(authorization)
        if not title.strip():
            return _safe_error("Missing field: title", 400)
        if not image.content_type or not image.content_type.startswith("image/"):
            return _safe_error("Uploaded file is not an image", 400)

        sb = get_admin_client()
        bucket = _env("SUPABASE_STORAGE_BUCKET")
        post_id = str(uuid4())
        ext = ""
        if image.filename and "." in image.filename:
            ext = "." + image.filename.split(".")[-1].lower()
        image_path = f"posts/{post_id}{ext}"
        image_bytes = await image.read()

        sb.storage.from_(bucket).upload(
            image_path,
            image_bytes,
            {"content-type": image.content_type, "upsert": "false"},
        )
        public_url = sb.storage.from_(bucket).get_public_url(image_path)

        insert_res = (
            sb.table("posts")
            .insert(
                {
                    "id": post_id,
                    "title": title.strip(),
                    "description": description.strip(),
                    "image_url": public_url,
                    "image_path": image_path,
                }
            )
            .execute()
        )
        post = (insert_res.data or [{}])[0]
        return {
            "post": {
                "id": post.get("id", post_id),
                "title": post.get("title", title.strip()),
                "description": post.get("description", description.strip()),
                "image_url": post.get("image_url", public_url),
                "created_at": post.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except HTTPException as exc:
        return _safe_error(exc.detail, exc.status_code)
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str, authorization: Optional[str] = Header(default=None)):
    try:
        require_admin(authorization)
        sb = get_admin_client()
        bucket = _env("SUPABASE_STORAGE_BUCKET")

        post_res = sb.table("posts").select("id,image_path").eq("id", post_id).limit(1).execute()
        if not post_res.data:
            return _safe_error("Post not found", 404)
        image_path = post_res.data[0].get("image_path")

        if image_path:
            sb.storage.from_(bucket).remove([image_path])

        sb.table("posts").delete().eq("id", post_id).execute()
        return {"ok": True}
    except HTTPException as exc:
        return _safe_error(exc.detail, exc.status_code)
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/comments")
def get_comments(postId: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("comments")
            .select("id,post_id,username,comment,created_at")
            .eq("post_id", postId)
            .order("created_at")
            .execute()
        )
        return {"comments": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/comments")
def add_comment(payload: Dict[str, Any]):
    try:
        post_id = str(payload.get("postId") or payload.get("post_id") or "").strip()
        username = str(payload.get("username") or "").strip()
        comment = str(payload.get("comment") or "").strip()

        if not post_id:
            return _safe_error("Missing postId", 400)
        if not username:
            return _safe_error("Missing username", 400)
        if not comment:
            return _safe_error("Missing comment text", 400)
        if len(username) > 32:
            return _safe_error("Username too long", 400)
        if len(comment) > 500:
            return _safe_error("Comment too long", 400)

        sb = get_admin_client()
        res = (
            sb.table("comments")
            .insert({"post_id": post_id, "username": username, "comment": comment})
            .execute()
        )
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
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/profiles/signup")
def signup(payload: Dict[str, Any]):
    try:
        username = str(payload.get("username") or "").strip()
        email = str(payload.get("email") or "").strip()
        password = str(payload.get("password") or "").strip()
        phone = str(payload.get("phone") or "").strip()
        dob = str(payload.get("dob") or "").strip()
        is_admin = bool(payload.get("is_admin", False))

        if not username:
            return _safe_error("Missing username", 400)
        if not email:
            return _safe_error("Missing email", 400)
        if not password:
            return _safe_error("Missing password", 400)
        if not phone:
            return _safe_error("Missing phone", 400)
        if not dob:
            return _safe_error("Missing date of birth", 400)
        if len(username) > 32:
            return _safe_error("Username too long", 400)
        if len(email) > 100:
            return _safe_error("Email too long", 400)
        if len(password) < 6:
            return _safe_error("Password must be at least 6 characters", 400)
        if len(phone) != 10 or not phone.isdigit():
            return _safe_error("Phone must be 10 digits", 400)
        if "@" not in email:
            return _safe_error("Invalid email format", 400)

        # Note: In production, you should hash the password before storing
        # For demo purposes, storing as-is (NOT RECOMMENDED FOR PRODUCTION)
        from hashlib import sha256
        hashed_password = sha256(password.encode()).hexdigest()

        sb = get_admin_client()
        res = (
            sb.table("profiles")
            .insert({
                "username": username, 
                "email": email, 
                "password": hashed_password,
                "phone": phone,
                "dob": dob,
                "is_admin": is_admin
            })
            .execute()
        )
        saved = (res.data or [{}])[0]
        return {
            "profile": {
                "id": saved.get("id"),
                "username": saved.get("username", username),
                "email": saved.get("email", email),
                "is_admin": saved.get("is_admin", is_admin),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/profiles/{username}")
def get_profile(username: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("profiles")
            .select("id,username,email,is_admin,created_at")
            .eq("username", username)
            .limit(1)
            .execute()
        )
        if not res.data:
            return _safe_error("Profile not found", 404)
        return {"profile": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/likes")
def get_likes(postId: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("likes")
            .select("id,post_id,username,created_at")
            .eq("post_id", postId)
            .execute()
        )
        return {"likes": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/likes")
def add_like(payload: Dict[str, Any]):
    try:
        post_id = str(payload.get("postId") or payload.get("post_id") or "").strip()
        username = str(payload.get("username") or "").strip()

        if not post_id:
            return _safe_error("Missing postId", 400)
        if not username:
            return _safe_error("Missing username", 400)
        if len(username) > 32:
            return _safe_error("Username too long", 400)

        sb = get_admin_client()
        res = (
            sb.table("likes")
            .insert({"post_id": post_id, "username": username})
            .execute()
        )
        saved = (res.data or [{}])[0]
        return {
            "like": {
                "id": saved.get("id"),
                "post_id": saved.get("post_id", post_id),
                "username": saved.get("username", username),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/likes")
def remove_like(payload: Dict[str, Any]):
    try:
        post_id = str(payload.get("postId") or payload.get("post_id") or "").strip()
        username = str(payload.get("username") or "").strip()

        if not post_id:
            return _safe_error("Missing postId", 400)
        if not username:
            return _safe_error("Missing username", 400)

        sb = get_admin_client()
        sb.table("likes").delete().eq("post_id", post_id).eq("username", username).execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/posts/{post_id}/with-stats")
def get_post_with_stats(post_id: str):
    try:
        sb = get_admin_client()
        
        # Get post
        post_res = (
            sb.table("posts")
            .select("id,title,description,image_url,created_at")
            .eq("id", post_id)
            .limit(1)
            .execute()
        )
        if not post_res.data:
            return _safe_error("Post not found", 404)
        post = post_res.data[0]

        # Get likes count
        likes_res = sb.table("likes").select("id").eq("post_id", post_id).execute()
        likes_count = len(likes_res.data or [])

        # Get comments
        comments_res = (
            sb.table("comments")
            .select("id,post_id,username,comment,created_at")
            .eq("post_id", post_id)
            .order("created_at")
            .execute()
        )

        return {
            "post": post,
            "stats": {
                "likes_count": likes_count,
                "comments_count": len(comments_res.data or [])
            },
            "comments": comments_res.data or []
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/auth/login")
def login(payload: Dict[str, Any]):
    try:
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "").strip()

        if not username or not password:
            return _safe_error("Missing username or password", 400)

        # Hash the password to compare with stored hash
        from hashlib import sha256
        hashed_password = sha256(password.encode()).hexdigest()

        sb = get_admin_client()
        res = (
            sb.table("profiles")
            .select("id,username,email,is_admin,password")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        if not res.data:
            return _safe_error("Invalid credentials", 401)

        profile = res.data[0]
        if profile.get("password") != hashed_password:
            return _safe_error("Invalid credentials", 401)

        # Create JWT token using Supabase auth
        client = get_anon_client()
        auth_resp = client.auth.sign_in_with_password({
            "email": profile.get("email"),
            "password": password
        })

        if hasattr(auth_resp, 'error') and auth_resp.error:
            return _safe_error("Login failed", 401)

        return {
            "user": {
                "id": profile.get("id"),
                "username": profile.get("username"),
                "email": profile.get("email"),
                "is_admin": profile.get("is_admin", False)
            },
            "token": auth_resp.session.access_token
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/expenses")
def get_expenses(view: str = "day", authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user:
            return _safe_error("Authentication required", 401)

        sb = get_admin_client()
        
        # Calculate date range based on view mode
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        if view == "day":
            start_date = today
        elif view == "month":
            start_date = today.replace(day=1)
        elif view == "year":
            start_date = today.replace(month=1, day=1)
        else:
            start_date = today
        
        # Get user's expenses and group expenses
        res = (
            sb.table("expenses")
            .select("id,description,amount,type,date,user_id,group_id,created_at")
            .gte("date", start_date.isoformat())
            .or_(f"user_id.eq.{current_user['id']},group_id.in.(select(id from expense_groups where created_by=eq.{current_user['id']}))")
            .order("date", desc=True)
            .execute()
        )
        return {"expenses": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/expenses")
def add_expense(payload: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user:
            return _safe_error("Authentication required", 401)

        description = str(payload.get("description") or "").strip()
        amount = float(payload.get("amount") or 0)
        expense_type = str(payload.get("type") or "").strip()
        date = str(payload.get("date") or "").strip()
        group_id = payload.get("group_id")

        if not description:
            return _safe_error("Missing description", 400)
        if amount <= 0:
            return _safe_error("Amount must be greater than 0", 400)
        if expense_type not in ["debit", "credit"]:
            return _safe_error("Type must be debit or credit", 400)
        if not date:
            return _safe_error("Missing date", 400)

        sb = get_admin_client()
        res = (
            sb.table("expenses")
            .insert({
                "description": description,
                "amount": amount,
                "type": expense_type,
                "date": date,
                "user_id": current_user["id"],
                "group_id": group_id
            })
            .execute()
        )
        saved = (res.data or [{}])[0]
        return {
            "expense": {
                "id": saved.get("id"),
                "description": saved.get("description", description),
                "amount": saved.get("amount", amount),
                "type": saved.get("type", expense_type),
                "date": saved.get("date", date),
                "user_id": saved.get("user_id", current_user["id"]),
                "group_id": saved.get("group_id", group_id),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id: str, payload: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user:
            return _safe_error("Authentication required", 401)

        # Check if user is admin or expense owner
        sb = get_admin_client()
        expense_res = (
            sb.table("expenses")
            .select("id,user_id")
            .eq("id", expense_id)
            .limit(1)
            .execute()
        )

        if not expense_res.data:
            return _safe_error("Expense not found", 404)

        expense = expense_res.data[0]
        is_admin = current_user.get("is_admin", False)
        is_owner = expense.get("user_id") == current_user["id"]

        if not (is_admin or is_owner):
            return _safe_error("Permission denied", 403)

        description = str(payload.get("description") or "").strip()
        amount = float(payload.get("amount") or 0)
        expense_type = str(payload.get("type") or "").strip()
        date = str(payload.get("date") or "").strip()
        group_id = payload.get("group_id")

        if not description:
            return _safe_error("Missing description", 400)
        if amount <= 0:
            return _safe_error("Amount must be greater than 0", 400)
        if expense_type not in ["debit", "credit"]:
            return _safe_error("Type must be debit or credit", 400)
        if not date:
            return _safe_error("Missing date", 400)

        res = (
            sb.table("expenses")
            .update({
                "description": description,
                "amount": amount,
                "type": expense_type,
                "date": date,
                "group_id": group_id
            })
            .eq("id", expense_id)
            .execute()
        )
        saved = (res.data or [{}])[0]
        return {
            "expense": {
                "id": saved.get("id", expense_id),
                "description": saved.get("description", description),
                "amount": saved.get("amount", amount),
                "type": saved.get("type", expense_type),
                "date": saved.get("date", date),
                "group_id": saved.get("group_id", group_id),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: str, authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user:
            return _safe_error("Authentication required", 401)

        # Check if user is admin or expense owner
        sb = get_admin_client()
        expense_res = (
            sb.table("expenses")
            .select("id,user_id")
            .eq("id", expense_id)
            .limit(1)
            .execute()
        )

        if not expense_res.data:
            return _safe_error("Expense not found", 404)

        expense = expense_res.data[0]
        is_admin = current_user.get("is_admin", False)
        is_owner = expense.get("user_id") == current_user["id"]

        if not (is_admin or is_owner):
            return _safe_error("Permission denied", 403)

        sb.table("expenses").delete().eq("id", expense_id).execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/expense-groups")
def get_expense_groups(authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user:
            return _safe_error("Authentication required", 401)

        sb = get_admin_client()
        res = (
            sb.table("expense_groups")
            .select("*")
            .eq("created_by", current_user["id"])
            .order("created_at", desc=True)
            .execute()
        )
        return {"groups": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/expense-groups")
def create_expense_group(payload: Dict[str, Any], authorization: Optional[str] = Header(default=None)):
    try:
        current_user = get_current_user(authorization)
        if not current_user or not current_user.get("is_admin", False):
            return _safe_error("Admin privileges required", 403)

        name = str(payload.get("name") or "").strip()
        description = str(payload.get("description") or "").strip()

        if not name:
            return _safe_error("Missing group name", 400)

        sb = get_admin_client()
        res = (
            sb.table("expense_groups")
            .insert({
                "name": name,
                "description": description,
                "created_by": current_user["id"]
            })
            .execute()
        )
        saved = (res.data or [{}])[0]
        return {
            "group": {
                "id": saved.get("id"),
                "name": saved.get("name", name),
                "description": saved.get("description", description),
                "created_by": saved.get("created_by", current_user["id"]),
                "created_at": saved.get("created_at", datetime.utcnow().isoformat()),
            }
        }
    except Exception as exc:
        return _safe_error(str(exc))

