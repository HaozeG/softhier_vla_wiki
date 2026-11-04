---
type: runbook
tags: [ingest, workflow]
sources: []
---
# Ingest a source

Use when adding a paper, doc, repo, or experiment result to the wiki. One source usually touches several notes, not one.

## Steps
0. **Choose the mode** ([wiki-design decision 0015](../decisions/0015-ingest-modes-brainstorm-or-in-depth.md)): before reading in detail, ask the user one question with two options:
   - **Brainstorming**: you read the whole source and run steps 1–11 automatically, then report the takeaways and a few check questions.
   - **In-depth**: the user opens the source beside the session and you lead them through it (below). Steps 2–11 follow the last section.

   The user can switch mode at any time: "faster" finishes the remaining sections automatically, and "slow down" switches to guided reading.
1. **Discuss:** tell the user the source's key takeaways and which notes you intend to create/update; adjust if they redirect you. In in-depth mode, this happens at the end of the reading, with the user's corrections folded in.
2. **Search first:** `tools/wiki.py find "<topic>"` — extend an existing note instead of duplicating it.
3. **Source note:** `tools/wiki.py new paper resources/<topic>/<slug>.md "<Title>"` (or `concept`/`entity` for non-papers). Fill every section faithfully; put the URL/ID in `sources:`. Leave no placeholder text behind. For an arXiv paper, read it with `tools/arxiv.py <id> -o <scratch>.md`: it turns arXiv's HTML rendering into Markdown with equations as their LaTeX and tables as cells, which PDF text extraction breaks; take numbers, equations and table rows from it. Without an HTML version, `tools/arxiv.py <id> --source -d <new empty dir>` fetches the LaTeX source. Keep that output outside the wiki, and use PDF page images only for figures. Keep it project-neutral: no "relevance to SoftHier-VLA" and no links into `knowledge/`; record scope caveats (device, precision, evidence tier) as claims of the source ([decision 0010](../decisions/0010-resources-stay-project-neutral.md)).
4. **Synthesize:** this is where the project reading goes. Update or create the `knowledge/` notes the source informs (`new concept knowledge/<slug>.md "<Title>"`; `new comparison …` for trade-off analyses). Where the new source contradicts or supersedes an existing claim, fix that note and say so in it, each citing the source note in `sources:` and linking to it.
5. **Glossary:** if the source introduces a standard term the notes will use, add a `field` row to the right group in `glossary/` (definition only, no numbers; then run `tools/wiki.py glossary --az` to refresh the A to Z index); a local meaning of a field term is a `convention` row.
6. **Diagram check:** for each touched `knowledge/` note with structure, add or update its ASCII diagram in the same edit as the text ([decision 0007](../decisions/0007-ascii-diagrams-as-logic-check.md)). Redraw from the new text; if the picture needs a box or arrow the text does not justify, or a case is missing, fix the text from the source note.
7. **Cross-link:** `tools/wiki.py related <each touched note>`; add relative links for every `NOT LINKED` neighbour that is genuinely related.
8. **Catalog:** add `- [Title](file.md) — one-line summary` per new note to its directory's `_overview.md`; revise `_abstract.md` if the directory's summary changed; repeat up the tree (`check` will flag parents).
9. **Decisions:** if the source changed a choice, write `new decision memories/decisions/NNNN-<slug>.md "<Title>"` (project decisions; wiki-design decisions go in `wiki-design/decisions/`).
10. **Verify:** `tools/wiki.py stamp <dirs>` → `index` → `health` (no errors; review every warning).
11. **Log:** when asked to commit: `tools/wiki.py commit ingest "<subject>" --source <url>`.

## In-depth mode: reading the source together
1. **Read it all first, yourself.** Then give a reading map: the sections in reading order, one line each on what the section contributes, and which parts to skim (related work, appendices, references).
2. **One section per turn.** Name exactly where to read (section number, page, figure or table) and give two or three things to look for, or a prediction to make before reading. Then stop and wait for the user.
3. **Check, then explain.** After the user has read, ask one check question (predict-then-read or explain-back). Explain new terms (look them up with `glossary "<term>"` first; note missing terms for step 5). Point out traps such as unlabeled figures, mixed measurement modes or internal inconsistencies.
4. **Draft that section's claims.** Write the section's key claims (with section, figure or table refs) as they will go in the source note, show them, and let the user correct them. Keep the drafts in the source note file as you go, so nothing is lost if the session ends.
5. **Move on only when the user says so.** The user's own questions and working conclusions go to session memory (mnemon), not the wiki, unless the source states them ([0013](../decisions/0013-scope-and-no-derived-content.md)). Critique of the source that the user wants kept (unclear points, weak arguments, unstated assumptions) goes into the source note's `## Reading notes (inference)` section, labelled as inference ([0015](../decisions/0015-ingest-modes-brainstorm-or-in-depth.md)).
6. **After the last section,** run steps 2–11. Show the diff of the knowledge notes before verifying.

After ingesting, run the periodic [health review](review-wiki-health.md).
