# Content Audit — InfoDogCats.com `posts` table

**Date:** 2026-08-02
**Scope:** All rows in Supabase `posts` table (`infodigcats23@gmail.com` project). No data was modified — this is a read-only diagnosis.
**Total posts:** 309

## Methodology

Every post's `title`, `slug`, `tags`, `excerpt`, and `content` length were pulled and run through a rule-based classifier, then manually reviewed for edge cases (all 18 titles mentioning both "dog" and "cat", plus a spot-check of every bucket for false positives/negatives). Classification rules, in order of precedence:

1. **`off_topic_geo`** — non-English content (French/German words or accented text detected in title/excerpt), or explicit US-only brand centricity (PetSmart, Chewy, BarkBox, Petco, Amazon).
2. **`off_topic_dogs`** — title is dog-specific (dog, puppy, canine, or a dog breed name) with no cat mention. Titles mentioning both species were reviewed by hand — kept as `relevant` where the content genuinely serves cat owners (e.g. "dog door" articles that are actually about cats using pet doors, dual-species product reviews), moved to `off_topic_dogs` where cats are only an incidental mention (e.g. dog-gate articles, "dog breeds that get along with cats").
3. **`low_quality`** — near-empty excerpt (e.g. excerpt is just the product name repeated, "Purina Pro", "Crate Furniture"), ALL-CAPS spammy titles, all-lowercase unpunctuated titles, or very thin article bodies (<2,500 characters).
4. **`relevant`** — everything else: cat care/health/breed/behaviour content and AU-market cat-for-sale/adoption content.

## Results

| Category | Count | % of total |
|---|---|---|
| `relevant` | 201 | 65.0% |
| `off_topic_dogs` | 88 | 28.5% |
| `low_quality` | 14 | 4.5% |
| `off_topic_geo` | 6 | 1.9% |

**Headline finding:** ~35% of the blog (108 of 309 posts) is either dog-only content, low-effort spun affiliate content, or non-AU/non-English content — almost certainly the cause of the topical-relevance and content-quality signals flagged in the site audit. Nearly all of the `off_topic_dogs` posts are still tagged with cat-related tags (`maine-coon`, `cat-breeds`, etc.) in the database, which suggests these were bulk-imported/scraped from a general pet-content feed and mistagged rather than written for this site — worth flagging as a data-hygiene issue independent of this cleanup.

## `off_topic_dogs` (88 posts) — dog-only content, no cat relevance

Example titles:
1. "The Ultimate Guide to Large Dog Shoes for All-Weather Protection"
2. "I Love Your French Bulldog Too 2024"
3. "How To Clean Dog Ears At Home Edition Step-by-Step Guide"
4. "Doggie doors best guide to freedom for Your dog"
5. "NEWFOUNDLAND THE ARISTOCRAT AMONG DOGS"

Full list: `content-audit-off-topic-dogs.json` (generated alongside this report).

## `off_topic_geo` (6 posts) — non-AU market or non-English

1. "The Best PetSmart Small Dog Rain Boots 2026" — US-only retailer (PetSmart)
2. "Russian White Cat Breed Facts, Traits, and Health" — excerpt is written in French ("Découvrez le Russian White Cat, un chat rare...")
3. "Large Dog Beds Amazon" — Amazon-centric, also dog content
4. "How to pause bark box" — BarkBox is a US-only subscription service
5. "Happy Cat Minkas Sterilised Geflügel 1,5kg" — German product listing, German-language content
6. "Outdoor Cat House Amazon: Best Shelters for Your Cat in 2025" — Amazon-centric

## `low_quality` (14 posts) — thin/spun content or unprofessional titles

1. "Purina Pro Plan High Protein Cat Food" — excerpt is literally "Purina Pro"
2. "HOW TO UNDERSTAND YOUR CAT BETTER" — ALL CAPS title
3. "ragdoll burmese cat" — unpunctuated lowercase title, no real subject
4. "6 things make your cat happy" — unpunctuated lowercase title
5. "Transformable Cat Tree" — excerpt is literally "Transformable Cat Tree" (thin/spun)

Full list: `content-audit-low-quality.json`.

## `relevant` (201 posts) — kept as-is

Example titles:
1. "7 Amazing Facts About Maine Coon Australia — Gentle Giants Down Under"
2. "Best Cat Food for Cats in Australia (2026): Top Vet-Recommended Picks"
3. "Sphynx Cat Breed in Australia: Care, Cost & Personality"
4. "Why Are Ragdoll Cats So Expensive?"
5. "Burmese Kittens for Sale in Melbourne Explained"

## Notes / open questions for Phase 2

- Dual-species titles (dog+cat, e.g. "7 Best Dog and Cat Doors for Your Pets", "Virbac EPIOTIC Ear Cleanser... For Dogs and Cats") were kept `relevant` since the product/content is genuinely usable by cat owners — flag if you'd rather prune these too.
- The `off_topic_dogs` tag mismatch (dog articles tagged `maine-coon`/`cat-breeds`) means the `/blog/tag/*` pages are also currently showing dog content under cat-breed tags — this will be fixed automatically once these posts are unpublished/noindexed in Phase 2, but worth being aware of.
- A separate, unrelated issue was noticed while reading `src/pages/[slug].astro`: unmatched slugs currently `302`-redirect to `/blog` rather than returning a real 404 — this is the mechanism behind the `about-us/` soft-404 mentioned in your brief. Will be addressed in Phase 3.

## Full data

Machine-readable classification of all 309 posts (id, title, slug, tags, category, reason) is saved at `content-audit-full.json` in the project root for reference during Phase 2.

**No database or code changes have been made. Awaiting approval to proceed to Phase 2.**
