---
description: Consult and update the SoftHier-VLA project wiki (the softhier_vla_wiki/ submodule). Use when you need what the project already knows or decided: terms and definitions, VLA and physical-AI concepts and techniques, source findings, past decisions; before design or planning work, and when a session produces a decision, a new term or a finding worth keeping.
---
# Project wiki

The wiki is the git submodule `softhier_vla_wiki/`: typed Markdown notes with tiered summaries, searchable with zvec. Run its tool by path from the project root (no venv activation): `softhier_vla_wiki/tools/wiki.py <command>`. If it says zvec is missing, run `softhier_vla_wiki/tools/wiki.py setup` once.

## Consult (before designing or deciding)
0. The session-start pointer lists terms this project defines locally. They override general knowledge: before using one, run `softhier_vla_wiki/tools/wiki.py glossary "<term>"` (or read `softhier_vla_wiki/glossary/`). Reveal only what the task needs: `ls <dir>` for one-line summaries, `find` for search. If you define a new term while designing, record it (see File back).
1. `softhier_vla_wiki/tools/wiki.py find "<question in plain words>"`; add `--under knowledge` or `--layer L0` to narrow. Browse with `ls <dir>`.
2. Read the L0/L1 hits first, open L2 notes only as needed. Prefer wiki content over guessing; cite `wiki://` URIs in plans.
3. Say plainly when the wiki has nothing relevant.

## File back (after a decision or finding)
Durable outcomes belong in the wiki, not only in chat:
1. `softhier_vla_wiki/tools/wiki.py new decision|concept|comparison <path> "<Title>"`, fill it fully. Put project decisions in `memories/decisions/NNNN-<slug>.md` (numbered from 0001), topic notes in `knowledge/`, and new sources in `resources/<topic>/` (source notes stay project-neutral: summarize what the source says, put what it means for SoftHier-VLA in `knowledge/`); do not write to `wiki-design/` (that is about the wiki itself). link related notes (`related <note>` shows candidates).
2. If a decision introduces or redefines a term, list it in the decision's `defines:` frontmatter and add a project row (`Term | Meaning | project | Defined in`) to `softhier_vla_wiki/glossary/project-terms.md` in the same commit; definitions only, no numbers or findings.
3. Where a note has structure (pipeline, tiers, timeline, decision tree), include one small ASCII diagram that shows the parts, the data between them (labelled arrows with sizes) and what repeats, matches the prose and adds no new claims (`softhier_vla_wiki/tools/diagram.py` builds aligned boxes); if drawing it exposes a gap in the text, fix the text (wiki `CLAUDE.md`, wiki-design decision 0007).
4. Run `softhier_vla_wiki/tools/wiki.py fmt` if you wrote a table (padded like Obsidian, decision 0008).
5. Add the catalog line to the directory's `_overview.md`, then `stamp`, `index`, `health` until clean.
6. Commit inside the submodule only when the user asks: `softhier_vla_wiki/tools/wiki.py commit update "<subject>"`. Never bump the parent's submodule pointer unasked.

Full conventions (note types, folder summary files, commit format, health review): `softhier_vla_wiki/CLAUDE.md`.
