import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'server',
  adapter: vercel({ webAnalytics: { enabled: true } }),
  integrations: [sitemap()],
  image: {
    remotePatterns: [{ protocol: 'https', hostname: '**.supabase.co' }],
  },
  vite: {
    plugins: [tailwindcss()],
  },
  site: 'https://www.infodogcats.com',
  trailingSlash: 'ignore',
});
