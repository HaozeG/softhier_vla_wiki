---
covers: c557ef090f82
---
# SoftHier-VLA wiki

Top-level map. Start here, drill down via each directory's `_overview.md`.

**Project side** (what we know and decided about SoftHier-VLA)
- `resources/` — 48 source notes in six topic folders (models, surveys, serving, compression, rk3588, hardware), tagged by evidence tier.
- `knowledge/` — synthesis on VLA edge serving; start with `vla-edge-serving-overview.md`.
- `memories/` — project memory; `memories/decisions/` holds project decision records (none yet).

**Wiki side** (how the wiki works)
- `wiki-design/` — decisions about the wiki and runbooks (ingest a source, review health).
- `tools/` — `wiki.py`, note templates, hooks, Claude Code plugin.

Change log: `tools/wiki.py log` (git). Health: `tools/wiki.py health`. Search: `tools/wiki.py find "..."`. Conventions: `CLAUDE.md`.
