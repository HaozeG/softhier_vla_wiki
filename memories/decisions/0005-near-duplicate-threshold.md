---
type: decision
tags: [lint, health, zvec, threshold]
sources: [memories/decisions/0002-lint-and-git-as-log.md, session:rk3588-ingest]
---
# 0005: Near-duplicate threshold raised to 0.93

## Context
`health` flags note pairs whose chunk embeddings have cosine similarity at or above a threshold (0.82 by default, set in [0002](0002-lint-and-git-as-log.md) from general expectations). After a first corpus of 38 source notes and 14 knowledge notes on one narrow topic (VLA serving), the default produced about 60 warnings, nearly all between distinct source notes that share vocabulary and structure. At 0.90 about 20 remained and included one non-duplicate pair (0.91); at 0.93 only one pair remained, and after cross-linking it was acknowledged. A test copy of a note with light rewording scored 1.00 against its original and was flagged at every threshold from 0.90 to 0.95.

## Decision
Default `DUP_THRESHOLD` is 0.93. Pairs that are already linked stay acknowledged, as before. When looking for overlap that is not a copy (a contradiction or a merge candidate), run `health --candidates` or lower the threshold temporarily. Resource notes are one per source and are never merged for similarity; a cross-link plus a "See also" line is the resolution.

## Why
A lint that fires on most pairs stops being read. A reworded copy scores near 1.0 with this embedding model, so 0.93 keeps the check able to catch real duplicates while letting a single-topic wiki pass. Revisit if the corpus broadens to unrelated topics (then a lower value is safe again) or if a real duplicate is found scoring between 0.85 and 0.93.
