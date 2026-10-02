---
covers: 82120ed318b8
---
# SoftHier-VLA wiki

Top-level map. Start order for newcomers: `README.md`, `glossary/_overview.md`, `knowledge/one-vla-call.md`, `knowledge/vla-edge-serving-overview.md`. Then drill down via each directory's `_overview.md`.

**Project side** (what we know and decided about SoftHier-VLA)
- `glossary/` — grouped term definitions; read it right after the README if terms are new. Convention and project terms are loaded into project sessions.
- `resources/` — 48 source notes in six topic folders (models, surveys, serving, compression, rk3588, hardware), tagged by evidence tier.
- `knowledge/` — synthesis on VLA edge serving; after the glossary read `one-vla-call.md`, then `vla-edge-serving-overview.md`.
- `memories/` — project memory; `memories/decisions/` holds project decision records (none yet).

**Wiki side** (how the wiki works)
- `wiki-design/` — decisions about the wiki and runbooks (ingest a source, review health).
- `tools/` — `wiki.py`, note templates, hooks, Claude Code plugin.

Change log: `tools/wiki.py log` (git). Health: `tools/wiki.py health`. Search: `tools/wiki.py find "..."`. Conventions: `CLAUDE.md`.
