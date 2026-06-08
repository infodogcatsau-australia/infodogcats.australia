export const prerender = false;
import type { APIRoute } from 'astro';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.PUBLIC_SUPABASE_URL;
const SUPABASE_SERVICE_ROLE = import.meta.env.SUPABASE_SERVICE_ROLE;

export const POST: APIRoute = async ({ request }) => {
  try {
    const { accessToken, catId, data } = await request.json();

    // التحقق من المستخدم
    const userSb = createClient(SUPABASE_URL, import.meta.env.PUBLIC_SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: `Bearer ${accessToken}` } }
    });
    const { data: { user }, error: userErr } = await userSb.auth.getUser();
    if (userErr || !user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401, headers: { 'Content-Type': 'application/json' }
      });
    }

    // التحقق أن الإعلان ملك للمستخدم ثم تحديثه
    const adminSb = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE);
    const { data: cat } = await adminSb.from('cats').select('user_id').eq('id', catId).single();
    
    if (!cat || cat.user_id !== user.id) {
      return new Response(JSON.stringify({ error: 'Forbidden' }), {
        status: 403, headers: { 'Content-Type': 'application/json' }
      });
    }

    const { error } = await adminSb.from('cats').update(data).eq('id', catId);
    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500, headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200, headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: 'Server error' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  }
};
