#!/usr/bin/env python3
"""
Create a clean backend without authentication
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
from dotenv import load_dotenv

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import Client, create_client

load_dotenv()

app = FastAPI(title="VPVS API - No Auth")

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


def _safe_error(message: str, status_code: int = 500) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


# Health endpoints
@app.get("/api/health")
@app.head("/api/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VPVS Backend API",
        "version": "2.0.0-1775806643"
    }


@app.get("/health")
@app.head("/health")
def root_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VPVS Backend API",
        "version": "2.0.0-1775806643"
    }


@app.get("/")
@app.get("/api")
@app.head("/")
@app.head("/api")
def index() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Posts endpoints
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
        res = sb.table("posts").select("*").eq("id", post_id).execute()
        if not res.data:
            return _safe_error("Post not found", 404)
        return {"post": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/posts")
def create_post(payload: Dict[str, Any]):
    try:
        sb = get_admin_client()
        post_data = {
            "id": str(uuid4()),
            "title": payload.get("title", ""),
            "description": payload.get("description", ""),
            "image_url": payload.get("image_url", ""),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "system"  # No auth, use system
        }
        res = sb.table("posts").insert(post_data).execute()
        return {"post": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("posts").select("*").eq("id", post_id).execute()
        if not res.data:
            return _safe_error("Post not found", 404)
        
        sb.table("posts").delete().eq("id", post_id).execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


# Comments endpoints
@app.get("/api/comments")
def get_comments(postId: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("comments")
            .select("id,post_id,username,comment,created_at")
            .eq("post_id", postId)
            .order("created_at", desc=True)
            .execute()
        )
        return {"comments": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/comments")
def get_all_comments():
    try:
        sb = get_admin_client()
        res = (
            sb.table("comments")
            .select("id,post_id,username,comment,created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return {"comments": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/comments")
def add_comment(payload: Dict[str, Any]):
    try:
        sb = get_admin_client()
        comment_data = {
            "id": str(uuid4()),
            "post_id": payload.get("post_id"),
            "username": payload.get("username", "anonymous"),
            "comment": payload.get("comment"),
            "created_at": datetime.utcnow().isoformat()
        }
        res = sb.table("comments").insert(comment_data).execute()
        return {"comment": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("comments").select("*").eq("id", comment_id).execute()
        if not res.data:
            return _safe_error("Comment not found", 404)
        
        sb.table("comments").delete().eq("id", comment_id).execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


# Likes endpoints
@app.post("/api/posts/{post_id}/like")
def like_post(post_id: str):
    try:
        sb = get_admin_client()
        # Check if already liked
        existing = sb.table("likes").select("*").eq("post_id", post_id).eq("username", "anonymous").execute()
        if existing.data:
            return _safe_error("Already liked", 400)
        
        like_data = {
            "id": str(uuid4()),
            "post_id": post_id,
            "username": "anonymous",
            "created_at": datetime.utcnow().isoformat()
        }
        res = sb.table("likes").insert(like_data).execute()
        return {"like": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/posts/{post_id}/like")
def unlike_post(post_id: str):
    try:
        sb = get_admin_client()
        res = sb.table("likes").select("*").eq("post_id", post_id).eq("username", "anonymous").execute()
        if not res.data:
            return _safe_error("Not liked", 400)
        
        sb.table("likes").delete().eq("post_id", post_id).eq("username", "anonymous").execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/posts/{post_id}/comments")
def get_post_comments(post_id: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("comments")
            .select("id,post_id,username,comment,created_at")
            .eq("post_id", post_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"comments": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/likes")
def get_all_likes():
    try:
        sb = get_admin_client()
        res = (
            sb.table("likes")
            .select("id,post_id,username,created_at")
            .order("created_at", desc=True)
            .execute()
        )
        return {"likes": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/posts/{post_id}/likes")
def get_post_likes(post_id: str):
    try:
        sb = get_admin_client()
        res = (
            sb.table("likes")
            .select("id,post_id,username,created_at")
            .eq("post_id", post_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"likes": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


# Expenses endpoints (no auth)
@app.get("/api/expenses")
def get_expenses():
    try:
        sb = get_admin_client()
        res = (
            sb.table("expenses")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/expenses")
def create_expense(payload: Dict[str, Any]):
    try:
        sb = get_admin_client()
        expense_data = {
            "id": str(uuid4()),
            "description": payload.get("description"),
            "amount": payload.get("amount"),
            "type": payload.get("type", "expense"),
            "date": payload.get("date"),
            "user_id": "system",  # No auth
            "group_id": payload.get("group_id"),
            "created_at": datetime.utcnow().isoformat()
        }
        res = sb.table("expenses").insert(expense_data).execute()
        return {"expense": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: str):
    try:
        sb = get_admin_client()
        sb.table("expenses").delete().eq("id", expense_id).execute()
        return {"ok": True}
    except Exception as exc:
        return _safe_error(str(exc))


# Expense groups endpoints (no auth)
@app.get("/api/expense-groups")
def get_expense_groups():
    try:
        sb = get_admin_client()
        res = (
            sb.table("expense_groups")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return {"groups": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/expense-groups")
def create_expense_group(payload: Dict[str, Any]):
    try:
        sb = get_admin_client()
        group_data = {
            "id": str(uuid4()),
            "name": payload.get("name"),
            "description": payload.get("description"),
            "created_by": "system",  # No auth
            "created_at": datetime.utcnow().isoformat()
        }
        res = sb.table("expense_groups").insert(group_data).execute()
        return {"group": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


# Profiles/Signup endpoints (no auth)
@app.get("/api/profiles")
def get_profiles():
    try:
        sb = get_admin_client()
        res = sb.table("profiles").select("*").execute()
        return {"profiles": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


@app.post("/api/profiles/signup")
def signup(payload: Dict[str, Any]):
    try:
        sb = get_admin_client()
        profile_data = {
            "id": str(uuid4()),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "dob": payload.get("dob"),
            "is_admin": payload.get("is_admin", False),
            "created_at": datetime.utcnow().isoformat()
        }
        res = sb.table("profiles").insert(profile_data).execute()
        return {"profile": res.data[0]}
    except Exception as exc:
        return _safe_error(str(exc))


@app.get("/api/profiles")
def get_profiles():
    try:
        sb = get_admin_client()
        res = sb.table("profiles").select("*").execute()
        return {"profiles": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))


# Simple login (no real auth)
@app.post("/api/auth/login")
def login(payload: Dict[str, Any]):
    try:
        username = payload.get("username")
        password = payload.get("password")
        
        if not username or not password:
            return _safe_error("Username and password required", 400)
        
        sb = get_admin_client()
        res = (
            sb.table("profiles")
            .select("*")
            .eq("username", username)
            .execute()
        )
        
        if not res.data:
            return _safe_error("User not found", 404)
        
        user = res.data[0]
        return {"user": user, "token": "mock-token-no-auth"}
    except Exception as exc:
        return _safe_error(str(exc))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
