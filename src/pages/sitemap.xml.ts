import type { APIRoute } from 'astro';
import { supabase } from '../lib/supabase';

export const GET: APIRoute = async () => {
  const BASE_URL = 'https://www.infodogcats.com';

  const cities = [
    'sydney', 'melbourne', 'brisbane', 'perth',
    'adelaide', 'gold-coast', 'canberra', 'hobart', 'darwin'
  ];

  const categories = ['cat-vet', 'cat-groomer', 'cat-shelter', 'pet-shop'];

  const staticPages = [
    { url: '/', priority: '1.0', changefreq: 'daily' },
    { url: '/cats-for-sale', priority: '0.9', changefreq: 'daily' },
    { url: '/blog', priority: '0.9', changefreq: 'daily' },
    { url: '/post-ad', priority: '0.8', changefreq: 'monthly' },
    { url: '/about', priority: '0.6', changefreq: 'monthly' },
    { url: '/contact', priority: '0.6', changefreq: 'monthly' },
    { url: '/privacy-policy', priority: '0.3', changefreq: 'yearly' },
    { url: '/terms', priority: '0.3', changefreq: 'yearly' },
    { url: '/login', priority: '0.4', changefreq: 'monthly' },
    { url: '/register', priority: '0.4', changefreq: 'monthly' },
  ];

  // Blog tag pages
  const tagPages = [
    'maine-coon', 'cat-breeds', 'cat-health', 'cat-food',
    'indoor-cats', 'feral-cats', 'ragdoll', 'burmese-cat',
    'sphynx-cat', 'kittens', 'rescue'
  ].map(tag => ({
    url: `/blog/tag/${tag}`,
    priority: '0.75',
    changefreq: 'weekly'
  }));

  // Near Me city pages
  const nearMeCityPages = cities.map(city => ({
    url: `/near-me/${city}`,
    priority: '0.8',
    changefreq: 'weekly'
  }));

  // Near Me category pages (9 × 4 = 36)
  const nearMeCategoryPages = cities.flatMap(city =>
    categories.map(cat => ({
      url: `/near-me/${city}/${cat}`,
      priority: '0.85',
      changefreq: 'weekly'
    }))
  );

  // Blog posts (noindex = false excludes pruned off-topic/geo content and posts
  // pending a content-quality rewrite — see content-audit.md)
  const { data: posts } = await supabase
    .from('posts')
    .select('slug, updated_at, published_at')
    .eq('is_published', true)
    .eq('noindex', false)
    .order('published_at', { ascending: false });

  const postPages = (posts || []).map((post: any) => ({
    url: `/${post.slug}`,
    priority: '0.7',
    changefreq: 'monthly',
    lastmod: post.updated_at || post.published_at
  }));

  // Cat listings
  const { data: cats } = await supabase
    .from('cats')
    .select('slug, updated_at, created_at')
    .eq('status', 'active')
    .eq('is_approved', true);

  const catPages = (cats || []).map((cat: any) => ({
    url: `/cats-for-sale/${cat.slug}`,
    priority: '0.8',
    changefreq: 'weekly',
    lastmod: cat.updated_at || cat.created_at
  }));

  // Individual service pages
  const categorySlugMap: Record<string, string> = {
    vet:      'vet',
    groomer:  'groomer',
    shelter:  'shelter',
    breeder:  'breeder',
    pet_shop: 'pet-shop',
  };

  const { data: services } = await supabase
    .from('local_services')
    .select('slug, city, category, created_at')
    .eq('is_active', true);

  const servicePages = (services || []).map((s: any) => ({
    url: `/near-me/${s.city.toLowerCase()}/${categorySlugMap[s.category] ?? s.category}/${s.slug}`,
    priority: '0.6',
    changefreq: 'monthly',
    lastmod: s.created_at,
  }));

  // Combine all
  const allPages = [
    ...staticPages,
    ...tagPages,
    ...nearMeCityPages,
    ...nearMeCategoryPages,
    ...postPages,
    ...catPages,
    ...servicePages,
  ];

  const today = new Date().toISOString().split('T')[0];

  const urlEntries = allPages.map(page => {
    const lastmod = (page as any).lastmod
      ? new Date((page as any).lastmod).toISOString().split('T')[0]
      : today;
    return `  <url>
    <loc>${BASE_URL}${page.url}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`;
  }).join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800',
    },
  });
};