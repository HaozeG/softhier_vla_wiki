---
type: decision
tags: [schema, layout, openviking, memory]
sources: [https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/02-context-types.md, https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/03-context-layers.md, https://github.com/volcengine/OpenViking/blob/main/docs/en/concepts/04-viking-uri.md, session:wiki-project-split]
---
# 0009: Keep project knowledge and wiki design in separate folders

## Context
Decisions 0001-0008 describe how the wiki itself works, yet they sat in `memories/decisions/`, the place project decisions belong. The plugin tells sessions in the parent repo to file their decisions there, so the first SoftHier-VLA decision would have been numbered 0009 beside "near-duplicate threshold". `resources/` had also grown to 48 notes in one folder (its catalog was 3607 of 4000 characters).

OpenViking, read from its own concept docs, separates three kinds of context: **resources** (knowledge added by the user, rarely changed, "organized by project or topic in directory hierarchy"), **memory** (durable knowledge the agent records and keeps updating; its built-in types include `events` for decisions and milestones, `entities` and `cases`), and **skills** (capability definitions, kept under the shared `agent/` scope for "capabilities and configuration"). Each directory carries a short abstract (L0) and an overview (L1).

## Decision
```text
softhier_vla_wiki/
|
|  PROJECT SIDE: what we know and decided about SoftHier-VLA
+-- resources/<topic>/    one faithful note per external source
|                         topics: models, surveys, serving, compression,
|                         rk3588, hardware
+-- knowledge/            synthesis built from the sources
+-- memories/decisions/   project decisions, numbered from 0001
|
|  WIKI SIDE: how the wiki works (not project content)
+-- wiki-design/
|   +-- decisions/        decisions 0001-0009 about the wiki itself
|   +-- runbooks/         ingest a source, review wiki health
+-- tools/                wiki.py, note templates, hooks, plugin
+-- CLAUDE.md README.md   operating manual, read by every session
```
- **Project side** holds only SoftHier-VLA content. Sessions in the parent repo write here: ingest into `resources/`, synthesize into `knowledge/`, record choices in `memories/decisions/`. Other memory types (for example `entities/` or `cases/`) are added when there is content for them, not before.
- **Wiki side** holds only material about the wiki. Sessions started in this repo change it; a project session uses the runbooks but does not edit `wiki-design/`.
- **Two number spaces.** Each decisions folder is numbered from 0001. In prose, cite "wiki-design decision 0007" or "project decision 0001", or link by path.
- **Resources by topic.** A new source goes in the topic folder that fits it; add a folder when a catalog nears the 4000-character limit.
- Decision 0004 (evidence tiers) stays on the wiki side: it is a rule for how sources are recorded, even though it names VLA sources.
- Claude's own personal memory (outside the repo) holds pointers about the user and working style only; anything the project needs later goes into the wiki.

How it maps to OpenViking: `resources/` = resources; `memories/decisions/` = memory `events`; `wiki-design/runbooks/` = skills (the wiki's own capabilities); `wiki-design/decisions/`, `tools/` and `CLAUDE.md` = system configuration (OpenViking's `agent/` scope). `knowledge/` has no OpenViking counterpart: it is the synthesis layer of the LLM-wiki pattern, kept apart from the sources it cites.

## Why
A project decision and a note on the lint threshold answer different questions and are read by different sessions; mixing them hides the project's own history and makes the plugin's "file back" instruction wrong. Following OpenViking's split keeps the sources, what was learned from them and what was decided as separate, browsable layers. Topic folders keep each catalog readable within its size limit.

Not adopted from OpenViking: its server (the wiki still has a vector database, but it is zvec running inside the tool with no server, see [0001](0001-wiki-layout-and-search.md)), hidden `.abstract.md` files (see [0006](0006-rename-folder-summary-files-and-plain-language.md)), and terms such as "soul", "peers" and "trajectories", which plain-words [0006](0006-rename-folder-summary-files-and-plain-language.md) argues against.

Builds on [0001](0001-wiki-layout-and-search.md) and [0004](0004-evidence-tiers-for-fast-moving-vla-sources.md).
