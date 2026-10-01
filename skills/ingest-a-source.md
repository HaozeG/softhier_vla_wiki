---
type: runbook
tags: [ingest, workflow]
sources: []
---
# Ingest a source

Use when adding a paper, doc, repo, or experiment result to the wiki. One source usually touches several notes, not one.

## Steps
1. **Discuss:** tell the user the source's key takeaways and which notes you intend to create/update; adjust if they redirect you.
2. **Search first:** `tools/wiki.py find "<topic>"` — extend an existing note instead of duplicating it.
3. **Source note:** `tools/wiki.py new paper resources/<slug>.md "<Title>"` (or `concept`/`entity` for non-papers). Fill every section faithfully; put the URL/ID in `sources:`. Leave no placeholder text behind.
4. **Synthesize:** update or create the `knowledge/` notes the source informs (`new concept knowledge/<slug>.md "<Title>"`; `new comparison …` for trade-off analyses). Where the new source contradicts or supersedes an existing claim, fix that note and say so in it, each citing the source note in `sources:` and linking to it.
5. **Diagram check:** for each touched `knowledge/` note with structure, add or update its ASCII diagram in the same edit as the text ([decision 0007](../memories/decisions/0007-ascii-diagrams-as-logic-check.md)). Redraw from the new text; if the picture needs a box or arrow the text does not justify, or a case is missing, fix the text from the source note.
6. **Cross-link:** `tools/wiki.py related <each touched note>`; add relative links for every `NOT LINKED` neighbour that is genuinely related.
7. **Catalog:** add `- [Title](file.md) — one-line summary` per new note to its directory's `_overview.md`; revise `_abstract.md` if the directory's summary changed; repeat up the tree (`check` will flag parents).
8. **Decisions:** if the source changed a choice, write `new decision memories/decisions/NNNN-<slug>.md "<Title>"`.
9. **Verify:** `tools/wiki.py stamp <dirs>` → `index` → `health` (no errors; review every warning).
10. **Log:** when asked to commit: `tools/wiki.py commit ingest "<subject>" --source <url>`.

After ingesting, run the periodic [health review](review-wiki-health.md).
