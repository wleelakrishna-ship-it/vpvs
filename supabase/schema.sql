-- Anti Gravity (Supabase / Postgres) schema + RLS
-- Apply in Supabase SQL editor (in order).

-- Extensions
create extension if not exists "pgcrypto";

-- Tables
create table if not exists public.posts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text not null default '',
  image_url text not null,
  image_path text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.posts(id) on delete cascade,
  username text not null,
  comment text not null,
  created_at timestamptz not null default now()
);

-- Indexes
create index if not exists posts_created_at_idx on public.posts (created_at desc);
create index if not exists comments_post_id_created_at_idx on public.comments (post_id, created_at asc);

-- Row Level Security
alter table public.posts enable row level security;
alter table public.comments enable row level security;

-- POSTS:
-- - Anyone can read posts (anon/public).
-- - No direct client writes. Create/delete go through Netlify functions using service role (bypasses RLS).
drop policy if exists "posts_select_public" on public.posts;
create policy "posts_select_public"
on public.posts
for select
to public
using (true);

-- COMMENTS:
-- - Anyone can read comments.
-- - Anyone can add comments (anon/public).
drop policy if exists "comments_select_public" on public.comments;
create policy "comments_select_public"
on public.comments
for select
to public
using (true);

drop policy if exists "comments_insert_public" on public.comments;
create policy "comments_insert_public"
on public.comments
for insert
to public
with check (
  char_length(username) between 1 and 32
  and char_length(comment) between 1 and 500
);

-- Optional hardening:
-- Prevent updates/deletes from clients (default denies; explicit deny not required).
-- You can also add stricter checks (rate limits should be handled at edge/API).

-- STORAGE:
-- Create a bucket named "images" in Supabase Storage.
-- Recommended bucket settings:
-- - Public: ON (so image URLs can be viewed without auth)
-- - MIME types: image/*
--
-- If you want RLS on storage.objects, you can enable "Public read" via policy in the Storage UI.
-- Uploads should remain server-side via Netlify Functions (service role) for admin-only.
