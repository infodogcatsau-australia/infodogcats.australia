# Content to rewrite — low-quality posts

These 14 posts are cat-relevant but currently too thin/spun/unprofessional to serve readers or the brand (see `content-audit.md` for classification methodology). As of Phase 2 they have been flagged `noindex = true` in Supabase (`posts` table) — **the URLs still resolve and the pages still render** (unlike the pruned off-topic content, these are not 301-redirected), but they:

- carry `<meta name="robots" content="noindex, follow">`
- are excluded from `/blog`, `/blog/tag/*`, and `sitemap.xml`

Once rewritten with real content, flip `noindex` back to `false` for that row and it will automatically reappear in listings/sitemap.

| Title | Slug | Issue |
|---|---|---|
| Purina Pro Plan High Protein Cat Food | `purina-pro-plan-high-protein-cat-food` | Excerpt is just "Purina Pro" — thin/spun |
| Why Does My Cat Lick Me? Exploring the Possible Reasons Behind This Common Feline Behavior | `why-does-my-cat-lick-me-exploring-the-possible` | Excerpt is just "Cat Lick Me" — thin/spun (also a near-duplicate of the unaffected post "Why Does My Cat Lick Me?") |
| HOW TO UNDERSTAND YOUR CAT BETTER | `how-to-understand-your-cat-better` | ALL CAPS spammy title |
| Vet's Best Flea and Tick Home Treatment Spray 32 oz | `vets-best-flea-and-tick-home-treatment-spray-32-oz` | Excerpt is just "Vet's Best Flea" — thin/spun; also reads as a dog-product review, confirm cat relevance when rewriting |
| Fancy Feast Grilled Wet Cat Food Seafood Collection in Wet Cat Food | `fancy-feast-grilled-wet-cat-food-seafood-collection-in-wet-cat-food` | Excerpt is just "Fancy Feast" — thin/spun; title also has a repeated "Wet Cat Food" |
| Dogs Are Man's Best Friend, but Cats Are a Pirate's First Mate | `dogs-are-mans-best-friend-but-cats-are` | Unprofessional/cutesy title, thin premise |
| Transformable Cat Tree | `transformable-cat-tree-with-good-price` | Excerpt is just "Transformable Cat Tree" — thin/spun |
| The Science of Why Do Cats Purr ? A Mysterious Sound of Self-Healing | `why-do-cats-purr` | Excerpt is just "Why Do Cats Purr ?" — thin/spun |
| Best Plato Cat and Dog 2024 | `best-plato-cat-and-dog-2024` | Broken-grammar, brand-name-spam title |
| Fussie Cat Grain Free Tuna and Salmon Canned Cat Food 2.82 Ounces | `fussie-cat-grain-free-tuna-and-salmon-canned-cat-food-2-82-ounces` | Excerpt is just "Fussie Cat" — thin/spun |
| ragdoll burmese cat | `ragdoll-burmese-cat` | Unpunctuated lowercase title, no clear subject |
| Purina Fancy Feast Gourmet Wet Cat Food Variety Pack Review | `purina-fancy-feast-gourmet-wet-cat-food-variety-pack-review` | Excerpt is just "Purina Fancy Feast" — thin/spun |
| 6 things make your cat happy | `6-things-make-your-cat-happy` | Unpunctuated lowercase title |
| Top 5 Breeds with Low Exercise Requirements | `top-5-breeds-with-low-exercise-requirements` | Excerpt is just "Top 5 Breeds" — thin/spun; title doesn't specify cat breeds, confirm cat relevance when rewriting |

**Not published, not deleted.** No further action needed until these are rewritten.
