---
covers: 82b3b1ca0501
---
# SoftHier-VLA wiki

Top-level map. Topic: physical AI (robots that perceive and act in the physical world); the first area covered is VLA models. Newcomers: read `README.md`, then the frame notes in `knowledge/` (SoftHier overview, one VLA call, VLA architecture, WAM stub), with `glossary/` open for new words. Then drill down via each directory's `_overview.md`.

**Project side** (what we know and decided about SoftHier-VLA)
- `glossary/` — grouped term definitions to look up while reading, with an A to Z index. Convention and project terms are loaded into project sessions.
- `resources/` — 14 source notes in two topic folders (models, surveys), tagged by evidence tier.
- `knowledge/` — synthesis on SoftHier and on VLA models (first area covered: how they are built); start with `softhier-and-the-project.md` and `one-vla-call.md`.
- `memories/` — project memory; `memories/decisions/` holds project decision records (none yet).

**Wiki side** (how the wiki works)
- `wiki-design/` — decisions about the wiki and runbooks (ingest a source, review health).
- `tools/` — `wiki.py`, note templates, hooks, Claude Code plugin.

Change log: `tools/wiki.py log` (git). Health: `tools/wiki.py health`. Search: `tools/wiki.py find "..."`. Conventions: `CLAUDE.md`.
