---
description: Consult and update the SoftHier-VLA project wiki (the softhier_vla_wiki/ submodule). Use when designing or planning, making architecture or implementation choices, asking what we already know or decided about SoftHier, VLA models, GEMM tiling, NoC or the simulator, reviewing past decisions, or when a session produces a decision or finding worth keeping.
---
# Project wiki

The wiki is the git submodule `softhier_vla_wiki/`: typed Markdown notes with tiered summaries, searchable with zvec. Run its tool by path from the project root (no venv activation): `softhier_vla_wiki/tools/wiki.py <command>`. If it says zvec is missing, run `softhier_vla_wiki/tools/wiki.py setup` once.

## Consult (before designing or deciding)
1. `softhier_vla_wiki/tools/wiki.py find "<question in plain words>"`; add `--under knowledge` or `--layer L0` to narrow. Browse with `ls <dir>`.
2. Read the L0/L1 hits first, open L2 notes only as needed. Prefer wiki content over guessing; cite `wiki://` URIs in plans.
3. Say plainly when the wiki has nothing relevant.

## File back (after a decision or finding)
Durable outcomes belong in the wiki, not only in chat:
1. `softhier_vla_wiki/tools/wiki.py new decision|concept|comparison <path> "<Title>"`, fill it fully, link related notes (`related <note>` shows candidates).
2. Where a note has structure (pipeline, tiers, timeline, decision tree), include one small ASCII diagram that matches the prose and adds no new claims; if drawing it exposes a gap in the text, fix the text (wiki `CLAUDE.md`, decision 0007).
3. Run `softhier_vla_wiki/tools/wiki.py fmt` if you wrote a table (padded like Obsidian, decision 0008).
4. Add the catalog line to the directory's `_overview.md`, then `stamp`, `index`, `health` until clean.
5. Commit inside the submodule only when the user asks: `softhier_vla_wiki/tools/wiki.py commit update "<subject>"`. Never bump the parent's submodule pointer unasked.

Full conventions (note types, folder summary files, commit format, health review): `softhier_vla_wiki/CLAUDE.md`.
