-- Phase 2: add noindex flag to posts table
-- Run this once in the Supabase SQL Editor (project sitmziehzhvqeftydtdr), then let Claude know.
-- This is the only step Claude cannot perform itself: the service-role key only grants
-- REST (data) access via PostgREST, not DDL/schema changes.

alter table posts add column if not exists noindex boolean not null default false;
create index if not exists posts_noindex_idx on posts(noindex);
