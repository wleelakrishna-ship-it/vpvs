import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import Client, create_client

app = FastAPI(title="Anti Gravity API")

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

    return {"id": getattr(user, "id", None)}


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

