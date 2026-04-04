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

create table if not exists public.likes (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.posts(id) on delete cascade,
  username text not null,
  created_at timestamptz not null default now(),
  unique(post_id, username)
);

create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  username text not null unique,
  email text not null unique,
  is_admin boolean not null default false,
  created_at timestamptz not null default now()
);

-- Indexes
create index if not exists posts_created_at_idx on public.posts (created_at desc);
create index if not exists comments_post_id_created_at_idx on public.comments (post_id, created_at asc);
create index if not exists likes_post_id_idx on public.likes (post_id);
create index if not exists profiles_username_idx on public.profiles (username);

-- Row Level Security
alter table public.posts enable row level security;
alter table public.comments enable row level security;
alter table public.likes enable row level security;
alter table public.profiles enable row level security;

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

-- LIKES:
-- - Anyone can read likes.
-- - Anyone can add/remove likes (anon/public).
drop policy if exists "likes_select_public" on public.likes;
create policy "likes_select_public"
on public.likes
for select
to public
using (true);

drop policy if exists "likes_insert_public" on public.likes;
create policy "likes_insert_public"
on public.likes
for insert
to public
with check (
  char_length(username) between 1 and 32
);

drop policy if exists "likes_delete_own" on public.likes;
create policy "likes_delete_own"
on public.likes
for delete
to public
using (username = auth.jwt() ->> 'username');

-- PROFILES:
-- - Users can view their own profile.
-- - Users can insert their own profile (signup).
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
on public.profiles
for select
to public
using (email = auth.jwt() ->> 'email');

drop policy if exists "profiles_insert_signup" on public.profiles;
create policy "profiles_insert_signup"
on public.profiles
for insert
to public
with check (
  char_length(username) between 1 and 32
  and char_length(email) between 5 and 100
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
