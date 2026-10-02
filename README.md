# Wiki for SoftHier-VLA

## What this wiki covers
Robots can now be steered by a vision-language-action (VLA) model: a program that reads camera images and a written instruction and answers with the commands that move the robot's arms. The wiki records what the literature says about running such models fast enough on the small chips inside robots, and what that means for mapping them onto SoftHier, a tile-based many-PE accelerator platform.

**New to the field? Read in this order:** this README, then the [glossary](glossary/_overview.md) (plain-words definitions), then [one VLA call, step by step](knowledge/one-vla-call.md) (one picture of what a model does each time the robot asks it), then the [VLA edge serving overview](knowledge/vla-edge-serving-overview.md) (findings and the full reading path). What the project itself is about: [SoftHier and the project](knowledge/softhier-and-the-project.md).

Agents should start at [CLAUDE.md](CLAUDE.md), which is the operating manual (note format, commands, workflows, commit format).

## How the wiki is built
An LLM-maintained wiki for the SoftHier-VLA project. It combines three ideas:

- **[OpenViking](https://github.com/volcengine/OpenViking)** — filesystem-as-context with tiered per-directory summaries (L0 abstract / L1 overview / L2 notes).
- **[zvec](https://github.com/alibaba/zvec)** — in-process vector DB for local hybrid search, related-note discovery and near-duplicate detection. No server, no API keys.
- **[Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** — sources → LLM-maintained linked wiki → schema, with ingest / query / lint, and a chronological log (here: git commit messages).

| Dir | Holds |
|---|---|
| `resources/<topic>/` | one faithful note per external source, grouped by topic (models, surveys, serving, compression, rk3588, hardware) |
| `glossary/` | grouped term definitions (field, convention, project scope); the plugin lists the names of convention and project terms at session start; definitions are looked up on demand (`wiki.py glossary`) |
| `knowledge/` | synthesized concept/entity notes; start with `one-vla-call.md`, then `vla-edge-serving-overview.md` |
| `memories/decisions/` | project decisions (numbered from 0001) |
| `wiki-design/` | how the wiki works: `decisions/` (wiki design records) and `runbooks/` (ingest a source, review health) |
| `tools/` | `wiki.py`, note templates (`concept entity paper decision runbook comparison`), commit-msg hook |
| `.claude/agents/wiki-health.md` | subagent that runs and triages `health` |

## Quick start
```bash
tools/wiki.py setup          # venv + deps + index + commit hook (once)
tools/wiki.py find "how do we tile GEMM"
tools/wiki.py health
tools/wiki.py log
```

## Use from a parent repo (Claude Code plugin)
`tools/claude-plugin/` is a Claude Code plugin (marketplace: `.claude-plugin/marketplace.json`): a SessionStart hook gives each session the wiki's summary and recent changes, and the `softhier-wiki:wiki` skill covers consulting it before design work and filing outcomes back. Install once per checkout, from the parent repo root (personal `local` scope; nothing to commit):
```bash
softhier_vla_wiki/tools/wiki.py setup
claude plugin marketplace add ./softhier_vla_wiki --scope local
claude plugin install softhier-wiki@softhier-wiki --scope local
```
Try without installing: `claude --plugin-dir softhier_vla_wiki/tools/claude-plugin`. The `wiki-health` subagent is deliberately not in the plugin; it belongs to sessions started inside this repo.

## Regular health checks
Invoke the `wiki-health` subagent (e.g. `Agent` with `subagent_type: wiki-health`), schedule it with Claude Code's `/schedule` or `/loop`, or run `tools/wiki.py health --strict` from cron/CI.
