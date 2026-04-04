-- WORKING SCHEMA - Copy and paste this into Supabase SQL Editor
-- This will fix the signup/login issues

-- Step 1: Drop all tables to start fresh
DROP TABLE IF EXISTS public.expenses CASCADE;
DROP TABLE IF EXISTS public.expense_groups CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;
DROP TABLE IF EXISTS public.likes CASCADE;
DROP TABLE IF EXISTS public.comments CASCADE;
DROP TABLE IF EXISTS public.posts CASCADE;

-- Step 2: Create tables in correct order
create table public.posts (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text not null default '',
  image_url text not null,
  image_path text not null,
  created_at timestamptz not null default now()
);

create table public.comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.posts(id) on delete cascade,
  username text not null,
  comment text not null,
  created_at timestamptz not null default now()
);

create table public.likes (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.posts(id) on delete cascade,
  username text not null,
  created_at timestamptz not null default now(),
  unique(post_id, username)
);

create table public.profiles (
  id uuid primary key default gen_random_uuid(),
  username text not null unique,
  email text not null unique,
  password text not null,
  phone text not null,
  dob date not null,
  is_admin boolean not null default false,
  created_at timestamptz not null default now()
);

create table public.expense_groups (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_by uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table public.expenses (
  id uuid primary key default gen_random_uuid(),
  description text not null,
  amount numeric not null check (amount >= 0),
  type text not null check (type in ('debit', 'credit')),
  date date not null,
  user_id uuid not null references public.profiles(id) on delete cascade,
  group_id uuid references public.expense_groups(id) on delete set null,
  created_at timestamptz not null default now()
);

-- Step 3: Create indexes
create index posts_created_at_idx on public.posts (created_at desc);
create index comments_post_id_created_at_idx on public.comments (post_id, created_at asc);
create index likes_post_id_idx on public.likes (post_id);
create index profiles_username_idx on public.profiles (username);
create index profiles_email_idx on public.profiles (email);
create index expenses_date_idx on public.expenses (date desc);
create index expenses_type_idx on public.expenses (type);
create index expenses_user_id_idx on public.expenses (user_id);
create index expenses_group_id_idx on public.expenses (group_id);
create index expense_groups_created_by_idx on public.expense_groups (created_by);

-- Step 4: Enable Row Level Security
alter table public.posts enable row level security;
alter table public.comments enable row level security;
alter table public.likes enable row level security;
alter table public.profiles enable row level security;
alter table public.expense_groups enable row level security;
alter table public.expenses enable row level security;

-- Step 5: Create RLS Policies
-- Posts: Anyone can read
create policy "posts_select_public" on public.posts for select to public using (true);

-- Comments: Anyone can read and insert
create policy "comments_select_public" on public.comments for select to public using (true);
create policy "comments_insert_public" on public.comments for insert to public with check (
  char_length(username) between 1 and 32 and char_length(comment) between 1 and 500
);

-- Likes: Anyone can read, insert, delete own
create policy "likes_select_public" on public.likes for select to public using (true);
create policy "likes_insert_public" on public.likes for insert to public with check (
  char_length(username) between 1 and 32
);
create policy "likes_delete_own" on public.likes for delete to public using (username = auth.jwt() ->> 'username');

-- Profiles: Users can insert own, view own
create policy "profiles_select_own" on public.profiles for select to public using (email = auth.jwt() ->> 'email');
create policy "profiles_insert_signup" on public.profiles for insert to public with check (
  char_length(username) between 1 and 32
  and char_length(email) between 5 and 100
  and char_length(password) >= 6
  and char_length(phone) = 10
  and dob <= current_date
);

-- Expense groups: Anyone can read, admins can insert
create policy "expense_groups_select_public" on public.expense_groups for select to public using (true);
create policy "expense_groups_insert_admin" on public.expense_groups for insert to public with check (
  exists (
    select 1 from public.profiles 
    where profiles.id = auth.uid() 
    and profiles.is_admin = true
  )
);

-- Expenses: Users can see own + groups, admins see all
create policy "expenses_select_user" on public.expenses for select to public using (
  user_id = auth.uid() 
  or exists (
    select 1 from public.profiles 
    where profiles.id = auth.uid() 
    and profiles.is_admin = true
  )
  or group_id in (
    select id from public.expense_groups 
    where created_by = auth.uid()
  )
);

create policy "expenses_insert_user" on public.expenses for insert to public with check (
  char_length(description) between 1 and 200
  and amount >= 0
  and type in ('debit', 'credit')
  and user_id = auth.uid()
);

create policy "expenses_update_admin" on public.expenses for update to public using (
  exists (
    select 1 from public.profiles 
    where profiles.id = auth.uid() 
    and profiles.is_admin = true
  )
) with check (
  char_length(description) between 1 and 200
  and amount >= 0
  and type in ('debit', 'credit')
);

create policy "expenses_delete_admin" on public.expenses for delete to public using (
  exists (
    select 1 from public.profiles 
    where profiles.id = auth.uid() 
    and profiles.is_admin = true
  )
  or user_id = auth.uid()
);

-- Step 6: Test data (optional)
-- You can run this to create a test admin user:
INSERT INTO public.profiles (username, email, password, phone, dob, is_admin) 
VALUES ('admin', 'admin@test.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '1234567890', '2000-01-01', true);

-- This creates a test regular user:
INSERT INTO public.profiles (username, email, password, phone, dob, is_admin) 
VALUES ('user', 'user@test.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '1234567890', '2000-01-01', false);

-- Note: The password hashes above are for 'password123'
