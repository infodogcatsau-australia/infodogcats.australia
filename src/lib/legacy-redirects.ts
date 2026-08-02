// Explicit old-slug -> new-path 301 redirects for known WordPress-era URLs.
//
// The only hard evidence available for this migration is url_mapping.txt, which only
// covers /wp-content/uploads/* image URLs (already handled by the R2 migration) — there
// is no surviving record (old sitemap, server logs, GSC export) of the WP site's page
// slugs. 'about-us' is confirmed (it's the URL that was found soft-404ing). The rest are
// standard WordPress default/plugin page slugs added defensively since they're extremely
// likely to have existed and cost nothing if unused.
//
// If Search Console's "Page with redirect" / 404 report surfaces more legacy URLs, add
// them here rather than letting them fall through to the catch-all 404.
export const LEGACY_REDIRECTS: Record<string, string> = {
  'about-us': '/about',
  'contact-us': '/contact',
  'terms-and-conditions': '/terms',
  'terms-of-service': '/terms',
  'terms-conditions': '/terms',
  'privacy': '/privacy-policy',
  'privacy-policy-2': '/privacy-policy',
  'sign-in': '/login',
  'sign-up': '/register',
  'log-in': '/login',
  'register-account': '/register',
};
