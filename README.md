# Anti Gravity

Minimal Facebook-style photo feed with:
- Frontend: React (Netlify)
- Backend: Python FastAPI on Vercel
- DB + Storage + Auth: Supabase

## Project structure

- `frontend/`: React app (feed, post detail, comments, admin login/dashboard)
- `backend/`: FastAPI serverless API for Vercel
- `supabase/`: SQL schema and RLS policies

## 1) Supabase setup

1. Create a Supabase project.
2. Run `supabase/schema.sql`.
3. Create a storage bucket named `images` (or update env var `SUPABASE_STORAGE_BUCKET`).
4. Keep bucket public for reads (or create equivalent storage read policy).

### Admin users

Admin-only APIs validate JWT and expect one of:
- `app_metadata.role = "admin"`
- `app_metadata.roles` containing `"admin"`

## 2) Backend (Python / Vercel)

### API endpoints

- `GET /api/posts`
- `GET /api/posts/{id}`
- `POST /api/posts` (admin; multipart title/description/image)
- `DELETE /api/posts/{id}` (admin)
- `GET /api/comments?postId=...`
- `POST /api/comments` (public)

### Backend env vars

Set in Vercel project settings (copy from `backend/.env.example`):
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`

### Deploy backend to Vercel

```bash
cd backend
vercel login
vercel --prod
```

## 3) Frontend (React / Netlify)

### Frontend env vars

Set in Netlify site env (copy from `frontend/.env.example`):
- `VITE_API_BASE_URL` (your Vercel backend URL, e.g. `https://your-api.vercel.app`)
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

### Deploy frontend to Netlify

1. Connect/import repo.
2. Set Base directory: `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add env vars above.

## 4) Local development

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Backend (for dependency check):
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

