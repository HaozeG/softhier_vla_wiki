---
type: decision
tags: [claude-code, plugin, workflow]
sources: [https://code.claude.com/docs/en/plugins]
---
# 0003: Claude Code plugin for parent-repo sessions

## Context
Work happens in a parent repo that embeds this wiki as a submodule. Docs alone do not make sessions consult it, and the user does not want usage enforced through documentation. Alternatives: a parent CLAUDE.md mandate (rejected: enforcement by docs), an MCP server (heavier; not needed yet), a per-prompt search hook (noisy; add only if needed).

## Decision
Ship a Claude Code plugin in `tools/claude-plugin/` with a marketplace at the wiki root. A SessionStart hook injects the wiki summary and recent changes (stdlib only, no model load, never fails); a `wiki` skill with a trigger-rich description covers consulting and filing back. Install per checkout at `local` scope. Keep `wiki-health` out of the plugin: it stays in `.claude/agents/` for sessions started in this repo.

## Why
Native mechanisms surface the wiki without mandating it, and unrelated prompts stay untouched. In a test, a design prompt that never mentioned the wiki ran `wiki.py find` first with the plugin; an unrelated edit did not. Without the plugin a small test repo was still greppable, so the benefit at scale is unproven. Revisit with a UserPromptSubmit hint if sessions skip the wiki in a large repo.

See also [0012](0012-glossary-with-on-demand-lookup.md): the hook also lists the glossary's local term names and points to on-demand lookup.

Builds on [0002](0002-lint-and-git-as-log.md) and [0001](0001-wiki-layout-and-search.md).
