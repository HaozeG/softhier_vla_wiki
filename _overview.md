---
covers: c33f918e47f1
---
# SoftHier-VLA wiki

Top-level map. Topic: physical AI (robots that perceive and act in the physical world); the first area covered is VLA models. Newcomers: read `README.md`, then `knowledge/one-vla-call.md`, then `knowledge/vla-edge-serving-overview.md` (which holds the full reading list), with `glossary/` open for new words. Then drill down via each directory's `_overview.md`.

**Project side** (what we know and decided about SoftHier-VLA)
- `glossary/` — grouped term definitions to look up while reading, with an A to Z index. Convention and project terms are loaded into project sessions.
- `resources/` — 48 source notes in six topic folders (models, surveys, serving, compression, rk3588, hardware), tagged by evidence tier.
- `knowledge/` — synthesis on VLA models (first area covered: how they are built, made efficient and served on robot hardware); start with `one-vla-call.md`, then `vla-edge-serving-overview.md`.
- `memories/` — project memory; `memories/decisions/` holds project decision records (none yet).

**Wiki side** (how the wiki works)
- `wiki-design/` — decisions about the wiki and runbooks (ingest a source, review health).
- `tools/` — `wiki.py`, note templates, hooks, Claude Code plugin.

Change log: `tools/wiki.py log` (git). Health: `tools/wiki.py health`. Search: `tools/wiki.py find "..."`. Conventions: `CLAUDE.md`.
