-- InfoDogCats Supabase Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- CATS table
create table if not exists cats (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references auth.users(id) on delete cascade,
  slug text unique not null,
  title text not null,
  breed text not null,
  price numeric(10,2) not null default 0,
  age_months int,
  description text,
  city text not null,
  state text not null,
  contact_phone text,
  contact_email text,
  status text not null default 'pending' check (status in ('pending','active','sold','expired','deleted')),
  is_approved boolean not null default false,
  views int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- CAT IMAGES table
create table if not exists cat_images (
  id uuid primary key default uuid_generate_v4(),
  cat_id uuid references cats(id) on delete cascade,
  storage_path text not null,
  is_primary boolean not null default false,
  sort_order int not null default 0,
  created_at timestamptz not null default now()
);

-- BLOG POSTS table
create table if not exists blog_posts (
  id uuid primary key default uuid_generate_v4(),
  slug text unique not null,
  title text not null,
  excerpt text,
  content_html text,
  cover_image_url text,
  category text,
  is_published boolean not null default false,
  published_at timestamptz,
  updated_at timestamptz not null default now(),
  read_time_minutes int,
  created_at timestamptz not null default now()
);

-- LOCAL SERVICES table
create table if not exists local_services (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  type text not null check (type in ('vet','groomer','pet_shop','boarding','other')),
  address text,
  city text not null,
  state text not null,
  phone text,
  website text,
  rating numeric(3,1),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-- CONTACT MESSAGES table
create table if not exists contact_messages (
  id uuid primary key default uuid_generate_v4(),
  name text,
  email text,
  message text not null,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

-- RPC: increment cat views
create or replace function increment_cat_views(cat_slug text)
returns void language plpgsql as $$
begin
  update cats set views = views + 1 where slug = cat_slug;
end;
$$;

-- INDEXES
create index if not exists cats_status_approved_idx on cats(status, is_approved);
create index if not exists cats_state_idx on cats(state);
create index if not exists cats_breed_idx on cats using gin(to_tsvector('english', breed));
create index if not exists cats_created_idx on cats(created_at desc);
create index if not exists cat_images_cat_id_idx on cat_images(cat_id);
create index if not exists blog_posts_slug_idx on blog_posts(slug);
create index if not exists blog_posts_published_idx on blog_posts(is_published, published_at desc);

-- ROW LEVEL SECURITY
alter table cats enable row level security;
alter table cat_images enable row level security;

-- Anyone can read active approved cats
create policy "Public read active cats" on cats for select using (status = 'active' and is_approved = true);
-- Users can insert their own cats
create policy "Users can insert cats" on cats for insert with check (auth.uid() = user_id);
-- Users can update their own cats
create policy "Users can update own cats" on cats for update using (auth.uid() = user_id);
-- Users can delete their own cats
create policy "Users can delete own cats" on cats for delete using (auth.uid() = user_id);

-- Cat images - public read
create policy "Public read cat images" on cat_images for select using (true);
-- Users can insert images for their own cats
create policy "Users can insert cat images" on cat_images for insert with check (
  exists (select 1 from cats where id = cat_id and user_id = auth.uid())
);

-- Blog posts - public read published
alter table blog_posts enable row level security;
create policy "Public read published posts" on blog_posts for select using (is_published = true);

-- Local services - public read active
alter table local_services enable row level security;
create policy "Public read active services" on local_services for select using (is_active = true);

-- Contact messages - anyone can insert
alter table contact_messages enable row level security;
create policy "Anyone can submit contact" on contact_messages for insert with check (true);

-- STORAGE bucket policy (run separately in Supabase dashboard or via API)
-- Create bucket: cat-images (public)
-- Policy: allow public read, allow authenticated upload
