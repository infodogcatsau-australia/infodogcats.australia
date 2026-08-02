# SEO & Content Cleanup — Summary of Changes

**Date:** 2026-08-02
**Scope:** `infodigcats-australia` (Vercel) / `sitmziehzhvqeftydtdr` (Supabase) / `infodigcatsau-australia/infodogcats.australia` (repo)

---

## Phase 1 — Content Audit (read-only)

Classified all 309 `posts` rows. Report: [content-audit.md](content-audit.md).

| Category | Count |
|---|---|
| `relevant` (kept) | 201 |
| `off_topic_dogs` | 88 |
| `low_quality` | 14 |
| `off_topic_geo` | 6 |

## Phase 2 — Content Pruning

**Database:** added `posts.noindex boolean not null default false` ([supabase-migration-phase2.sql](supabase-migration-phase2.sql), run manually in the Supabase SQL Editor — the service-role key only grants PostgREST data access, not DDL). Set `noindex = true` on 108 rows (94 off-topic + 14 low-quality). No rows hard-deleted — all preserved for backlink history.

**Code:**
- [src/lib/pruned-posts.ts](src/lib/pruned-posts.ts) — 94 off-topic slugs; both article routes 301-redirect these straight to `/blog`, before any DB query
- [src/lib/legacy-redirects.ts](src/lib/legacy-redirects.ts) *(Phase 3, see below)*
- [src/pages/[slug].astro](src/pages/[slug].astro), [src/pages/blog/[slug].astro](src/pages/blog/[slug].astro) — pass `noindex` through to `Layout`
- [src/components/Layout.astro](src/components/Layout.astro), [src/components/SEOMeta.astro](src/components/SEOMeta.astro) — new `noindex` prop → `<meta name="robots" content="noindex, follow">`
- [src/pages/blog/index.astro](src/pages/blog/index.astro), [src/pages/blog/tag/[tag].astro](src/pages/blog/tag/[tag].astro), [src/pages/sitemap.xml.ts](src/pages/sitemap.xml.ts) — filter `.eq('noindex', false)`
- [content-to-rewrite.md](content-to-rewrite.md) — the 14 low-quality posts, still live at their URLs (not redirected) pending a rewrite

**Result:** 94 dead URLs now 301 → `/blog`; 108 posts excluded from `/blog`, tag pages, and the sitemap; 201 relevant posts unaffected.

## Phase 3 — Soft-404 Fix

**Root cause found:** `src/pages/[slug].astro` (and its near-duplicate `src/pages/blog/[slug].astro`, plus `src/pages/blog/tag/[tag].astro`) all `302`-redirected any unmatched slug to `/blog` — this is what made `about-us/` (and any other broken URL) resolve as a `200` with duplicate blog-listing content.

**Fix:**
- [src/pages/404.astro](src/pages/404.astro) — new, real 404 page: `Astro.response.status = 404`, distinct content, `noindex`
- All three routes above now use `Astro.rewrite('/404')` for anything genuinely unmatched — never a redirect
- [src/lib/legacy-redirects.ts](src/lib/legacy-redirects.ts) — explicit 301 map for known WordPress-era slugs, checked before falling through to 404. Only `about-us` is evidence-backed (the confirmed broken URL); the rest (`contact-us`, `terms-and-conditions`, `sign-in`, etc.) are standard WP default slugs added defensively. **No old sitemap/server-log/GSC export was available** to build a complete legacy URL list — recommend pulling Search Console's 404 report to extend this map with real data.

**Verified live** (not just read from code): `/about-us/` → `301` → `/about`; `/contact-us` → `301` → `/contact`; unknown slug → real `404`; WP date-permalink style URL (`/2023/03/11/...`) → real `404`; a Phase 2 pruned slug → still `301` → `/blog`; unknown blog tag → real `404`.

## Phase 4 — Cats Table Cleanup

Queried `cats` (34 rows). Found 27 test/demo rows (regex `-(test|demo)-?[0-9]*$` on slug) and, after your review, 6 more rows misspelling "Sydney" (`Syndeny` ×5, `SYDENY` ×1) with a **city/state mismatch confirming they were junk/spam submissions**, not typo'd genuine listings — you approved deleting all 6 as junk rather than correcting them.

**Deleted (permanent, approved):**
- 33 `cats` rows
- 33 `cat_images` rows (cascaded automatically via existing `on delete cascade` FK)
- 33 R2 objects (26 shared `demo/NN-breed.jpg` fixtures + 7 real uploaded images from the junk listings, deleted via `DeleteObjectsCommand`)

**Result:** 1 `cats` row remains — `gorgeous-maine-coon-kitten-sydney-nsw-2026` (Sydney, NSW, correctly spelled, `active`/`approved`). This is the only real listing currently on the site — worth noting as a business/inventory concern distinct from this SEO cleanup: the marketplace has no other live seller listings.

## Phase 5 — Post-Execution Verification

- **`robots.txt`**: didn't exist anywhere in the project. Created [public/robots.txt](public/robots.txt) — allows all indexable content, disallows `/api/`, `/auth/`, `/dashboard`, `/edit-ad/`, references the sitemap.
- **Sitemap**: regenerated and checked programmatically against the audit data — **1,268 URLs total**, exactly **1** `cats-for-sale` listing URL (the one real listing), **0** off-topic/low-quality post URLs, **0** test/demo cat URLs, **210** root-level URLs (201 relevant posts + 9 single-segment static pages — matches expected count exactly).
- **Homepage**: re-rendered `/` — "Fresh Listings" shows only the one real listing, no demo/test content present.

---

## Files added/changed

**New:**
`content-audit.md`, `content-audit-full.json`, `content-audit-off-topic-dogs.json`, `content-audit-off-topic-geo.json`, `content-audit-low-quality.json`, `content-to-rewrite.md`, `supabase-migration-phase2.sql`, `changes-summary.md`, `src/lib/pruned-posts.ts`, `src/lib/legacy-redirects.ts`, `src/pages/404.astro`, `public/robots.txt`

**Modified:**
`src/components/Layout.astro`, `src/components/SEOMeta.astro`, `src/pages/[slug].astro`, `src/pages/blog/[slug].astro`, `src/pages/blog/index.astro`, `src/pages/blog/tag/[tag].astro`, `src/pages/sitemap.xml.ts`

**Database:**
`posts.noindex` column added; 108 rows flagged `noindex = true`; 33 `cats` rows + cascaded `cat_images` deleted.

**Not yet done, flagged for you:**
- 14 low-quality posts need an actual rewrite (`content-to-rewrite.md`)
- Legacy redirect map (`src/lib/legacy-redirects.ts`) is only evidence-backed for one URL — extend from Search Console's 404 report if you have access
- Only 1 real cat listing exists site-wide post-cleanup — an inventory gap, not an SEO one

None of this has been committed or deployed — it's sitting as local changes for your review.
