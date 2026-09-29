---
type: decision
tags: [evidence, trust, ingest, conventions, vla]
sources: [resources/vla-perf.md, resources/figure-helix.md, resources/litevla-edge.md, resources/lightvla.md, resources/jetson-pi.md]
---
# 0004: Evidence tiers for fast-moving VLA sources

## Context
VLA efficiency literature moves within weeks: several relevant papers were posted only days to months before the first ingest, with few citations, while other useful facts come from vendor pages, forum posts and company blogs. The first ingest also met a web-search summary that attributed specific claims (4-bit quantization, wattage, a 23× saving) to a company page that, when fetched, did not contain them; and papers whose headline numbers depend on a reproduced baseline, a copied baseline latency, or an unstated device. Notes must stay trustworthy for newcomers without inventing reviewer status or dates (git records dates).

## Decision
1. **Read primary text before writing a source note.** Every number in a `resources/` note comes from the paper or page text (page, table or section cited); search summaries and third-party blurbs are leads, not sources.
2. **Tag by evidence tier**, using tags on the source note: `recent` for papers posted within a few months of ingest or without independent reproduction (state "posted <month year>" from the arXiv metadata, no relative ages); `low-evidence` for sources with latency-only claims, unclear devices or no task success; `first-party` for vendor or company pages (marketing-level unless numbers are given); `community` for forum posts.
3. **Record the caveat next to the claim:** baseline reproduced vs published, baseline latency copied from another paper, hardware unspecified, roofline vs measurement, sparse vs dense TOPS, simulation-only.
4. **Unverified claims are excluded** and, if they circulated, named once in the relevant source note as unverified (as done for Helix).
5. **Knowledge notes lead with claims supported by more than one source or by a primary measurement,** label estimates as estimates ([edge budget estimate](../../knowledge/edge-budget-estimate.md)), and list sources by wiki path.

## Why
It keeps the wiki usable for judging a field where rankings shift quickly, and stops secondary summaries from compounding. Recording tier at the source keeps knowledge notes short. Revisit if the tag vocabulary proves too coarse (for example, split `recent` by whether a code release exists) or once `health` can lint for missing caveats.
