import { createClient } from '@supabase/supabase-js';
import { createServerClient, parseCookieHeader, serializeCookieHeader } from '@supabase/ssr';
import { getR2PublicUrl } from './r2';

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

// Client-side (browser)
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  }
});

// Server-side (Astro pages) — lit les cookies de la request
export function createSupabaseServerClient(request: Request, responseHeaders: Headers) {
  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return parseCookieHeader(request.headers.get('Cookie') ?? '');
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => {
          responseHeaders.append(
            'Set-Cookie',
            serializeCookieHeader(name, value, options)
          );
        });
      },
    },
  });
}

export function getImageUrl(path: string, width = 800): string {
  if (!path) return '/placeholder-cat.jpg';
  return getR2PublicUrl(path);
}

export function getThumbnailUrl(path: string): string {
  return getImageUrl(path, 400);
}