import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  }
});

export function getImageUrl(path: string, width = 800): string {
  if (!path) return '/placeholder-cat.jpg';
  return `${supabaseUrl}/storage/v1/render/image/public/cat-images/${path}?width=${width}&quality=80&format=webp`;
}

export function getThumbnailUrl(path: string): string {
  return getImageUrl(path, 400);
}
