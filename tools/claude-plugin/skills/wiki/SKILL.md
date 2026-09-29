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
2. Add the catalog line to the directory's `.overview.md`, then `stamp`, `index`, `health` until clean.
3. Commit inside the submodule only when the user asks: `softhier_vla_wiki/tools/wiki.py commit update "<subject>"`. Never bump the parent's submodule pointer unasked.

Full conventions (note types, sidecars, commit format, health review): `softhier_vla_wiki/CLAUDE.md`.
