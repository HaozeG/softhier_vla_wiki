# Wiki conventions (read before editing)

An LLM-maintained wiki for SoftHier-VLA. You (the agent) own the wiki: you write and maintain it, the human curates sources and asks questions. The point is **compounding**: knowledge is synthesized once into linked, structured notes and kept current, not re-derived from raw sources on every question.

## Architecture
| Layer | Where | Rule |
|---|---|---|
| Sources | raw files (PDFs, data) you are given; `resources/<topic>/` holds one faithful note per source (topics: models, surveys, serving, compression, rk3588, hardware; add a topic folder when a catalog nears its limit) | Raw files are immutable: read, never modify. Source notes: correct errors, don't editorialize. **A source note records what the source says (summary, claims with section/figure refs, caveats) and never discusses SoftHier-VLA**: no "relevance", "implications" or links into `knowledge/` ([decision 0010](wiki-design/decisions/0010-resources-stay-project-neutral.md)) |
| Glossary (project side) | `glossary/` (grouped term definitions: scope `field`, `convention`, `project`) | Definitions only, no numbers or findings. Convention and project terms are loaded into project sessions by the plugin ([decision 0012](wiki-design/decisions/0012-glossary-loaded-by-the-plugin.md)) |
| Wiki (project side) | `knowledge/` (synthesis: what the sources mean for SoftHier-VLA, incl. design implications), `memories/decisions/` (project decisions) | You maintain it; every note cross-linked and cited; the only place project discussion lives |
| Wiki design (wiki side) | `wiki-design/decisions/` (decisions about the wiki), `wiki-design/runbooks/`, `tools/` | Kept apart from project content ([decision 0009](wiki-design/decisions/0009-separate-project-knowledge-from-wiki-design.md)); changed only by wiki-development sessions |
| Schema | this file, `tools/templates/`, `tools/wiki.py` (lint) | Follow it; propose changes via a decision record |

Every folder has two short summary files: `_abstract.md` (≤256 chars, the one-glance summary; also called L0) and `_overview.md` (≤4000 chars, also the *catalog*: every note gets a line `- [Title](file.md) — one-line summary`; also called L1). Read these first, open the full notes (L2) only when needed. The layering comes from OpenViking. **Git is the log**; zvec is the search index that finds related notes by meaning.

## Note format (enforced by `check`)
```
---
type: concept | entity | paper | decision | runbook | comparison
tags: [a, b]
sources: [url, wiki-path, or session:<name>]   # required non-empty for concept/entity/paper
---
# Title
## <required sections for the type>
```
Required `##` sections: concept/entity → `Summary`; paper → `Summary`, `Key claims`; decision → `Context`, `Decision`, `Why`; runbook → `Steps`; glossary → `Summary`, `Terms` (a table `Term | Meaning | Scope | Defined in`); comparison → `Summary`, `Comparison` (a table; use for analysed questions such as design trade-offs). Scaffold with `tools/wiki.py new <type> <path> "<Title>"`. Rules: one topic per note; claim first; short paragraphs/lists; relative links to related notes; no dates in files (git records them); no `TODO` left behind; never invent facts — cite `sources:`; use plain words over jargon, and define any unavoidable term the first time it appears ([decision 0006](wiki-design/decisions/0006-rename-folder-summary-files-and-plain-language.md)).

**Diagrams ([decision 0007](wiki-design/decisions/0007-ascii-diagrams-as-logic-check.md)).** A note whose content has structure (pipeline, timeline, tiers, decision tree, taxonomy, dataflow) carries one ```` ```text ```` ASCII diagram, usually right after `## Summary`: plain ASCII, ≤80 columns, ~25 lines, no line starting with `#`. The diagram adds no claim and no number the text lacks; text and diagram change in the same edit. Show the parts (boxes), the data between them (labelled arrows with sizes) and what repeats (a drawn xN loop, once-per-call vs per-step); build boxed layouts with `tools/diagram.py` ([decision 0011](wiki-design/decisions/0011-diagrams-show-parts-data-and-repetition.md)). Drawing it is a second check on the prose: if a case is missing, an arrow contradicts a sentence, or quantities do not add up, fix the text from the cited source and say so in the commit body. Not for tables of numbers, `resources/` notes, or `_abstract.md`/`_overview.md`.

**Tables ([decision 0008](wiki-design/decisions/0008-obsidian-padded-tables.md)).** Store pipe tables padded the way Obsidian does (the maintainer views the wiki there, and it would otherwise rewrite them). After editing a table run `tools/wiki.py fmt`; `check` warns `TABLEFMT` otherwise.

## The three operations
- **Ingest** a source → follow `wiki-design/runbooks/ingest-a-source.md`. First tell the user the key takeaways and what you plan to touch. One source touches several notes (often 10–15): source note, the knowledge notes it informs, cross-links, catalog entries, decisions.
- **Query** → `find "<question>"` (hybrid semantic + keyword), `ls`/`tree` to browse, read L0/L1 then the L2 hits. Answer from the wiki and cite `wiki://` URIs. If the answer is a valuable synthesis, **file it back** as a note (a good answer that stays in chat is lost).
- **Lint** → `tools/wiki.py health` (or the `wiki-health` subagent); procedure in `wiki-design/runbooks/review-wiki-health.md`. Covers duplicates, contradictions, stale claims superseded by newer sources, orphans, concepts that deserve their own page, and data gaps. Run after large ingests and periodically.

## zvec is for what `ls`/`grep` can't do
`find` — meaning-based retrieval (its scores are rank-fusion values ≈0.03 max, only their order matters; `related`/`health` print cosine similarities) ("how do we split GEMM across tiles" matches notes that never say "split"). `related <note>` — nearest-neighbour notes, flagged `NOT LINKED`: use it on every ingest to find where to cross-link. `health` — near-duplicate detection (`NEARDUP`) across notes. Use `grep`/`ls` for exact strings and paths; use zvec for similarity, overlap, and missing links.

## Commands (`tools/wiki.py`, venv active)
| Command | Purpose |
|---|---|
| `find "<q>" [-n N] [--layer L0\|L1\|L2] [--under <dir>] [--width N]` | Hybrid search (snippets truncated; `--width` widens; open the file for detail) |
| `related <note> [-n N]` | Similar notes, `linked` / `NOT LINKED` |
| `ls [<dir>] [-d N]` / `tree [<dir>] [-d N]` | Browse with L0 abstracts |
| `new <type> <path> "<Title>"` | Scaffold a note from `tools/templates/` |
| `index` | Sync the search index with the files (incremental) |
| `check [--strict]` | Fast structural lint, no model: folder summary files (missing, empty, stale, too long), frontmatter, sections, links, catalog, diagrams (`DIAGRAM`: over 80 columns or non-ASCII), table padding (`TABLEFMT` warning), unfilled template comments, orphans, TODOs, exact duplicates |
| `health [--strict] [--dup-threshold 0.93] [--candidates]` | `index` + `check` + zvec near-duplicate detection; `--candidates` also lists related-but-distinct pairs to read for contradictions |
| `glossary ["<term>"] [--loaded]` | Look up glossary terms; `--loaded` prints the convention and project terms the plugin injects at session start |
| `fmt [--check]` | Pad all pipe tables like Obsidian (whitespace only, idempotent); `--check` just reports |
| `stamp [<dirs>]` | Record the folder's content hash in its summary files after you rewrite them |
| `commit <op> "<subject>" [--source URL]... [--body ...] [--dry-run]` | Lint-gated commit with structured message |
| `log [-n N] [--op OP] [--path P] [--pages]` / `history <note>` | Read the change log back from git |
| `setup` | One-time: create `.venv`, install deps, build the index, enable the hook (works from any cwd, e.g. `softhier_vla_wiki/tools/wiki.py setup`) |
| `install-hooks` | Enable the `commit-msg` hook that enforces the format below |

## Write workflow (every insert / update / delete)
1. Edit notes. A decision that introduces or redefines a term lists it in its `defines:` frontmatter and adds a project row to `glossary/project-terms.md` in the same commit (`check` reports `DEFINES`); a source that brings a new standard term adds a `field` row to the right glossary group. Glossary rows are definitions only: no measured or derived numbers, examples or findings (`check` reports `GLOSSARY`). Update the directory's `_overview.md` (catalog line) and `_abstract.md` if its summary changed; parents too.
2. `fmt` (if you touched a table) → `stamp <dirs>` → `check`. Staleness cascades upward: a directory's hash includes its children's L0 abstracts, so changing `knowledge/_abstract.md` flags the root summary files too; review them and stamp (`stamp .` for root). Re-stamping an accurate sidecar is fine. Replace placeholder text such as "Empty until populated" when adding the first note.
3. `index` → `health`; no errors, and every warning read (`NEARDUP`: merge or cross-link; `ORPHAN`: link via `related`).
4. **Delete** = remove the file, its catalog line, and links to it (`check` finds the rest).
5. Commit (op: `ingest` = a new external source; `update` = new/changed knowledge or decisions from our own work; `delete`; `lint` = health fixes; `refactor` = restructuring; `init` = first commit). Only commit when the user asked you to, or in an autonomous maintenance run): `tools/wiki.py commit <op> "<subject>"`.

## Git as the log
One logical operation = one commit; the message is the dated record. Format (enforced by hook + `commit`):
```
wiki(<ingest|update|delete|lint|refactor|init>): <imperative subject>

<optional why>

Date: YYYY-MM-DD
Op: ingest
Pages: A knowledge/x.md; M resources/y.md
Sources: <url>; <url>
```
`commit` fills `Date`/`Op`/`Pages`/`Sources` for you and refuses if `check` has errors. Read back: `log --op ingest`, `log --pages`, `history knowledge/x.md`, or plain `git log --grep '^wiki('`. Never put dates inside notes.

## Two ways this wiki is used
The Claude Code plugin in `tools/claude-plugin/` (see README) makes parent-repo sessions aware of the wiki: a SessionStart hook injects its summary and recent changes, and a `softhier-wiki:wiki` skill covers consulting and filing back.

- **Wiki-development session** (started in this repo): improves the schema/tooling, runs `wiki-health`, curates structure. Writes to the wiki side (`wiki-design/`, `tools/`, `CLAUDE.md`). The `wiki-health` subagent (`.claude/agents/`) is discoverable only from here.
- **Working session in the parent repo** (this repo is its `softhier_vla_wiki/` submodule): queries the wiki and files updates while doing other work (e.g. design plans). Writes only to the project side: `resources/`, `knowledge/` and project decisions in `memories/decisions/` (numbered from 0001; wiki-design decisions have their own numbers, so cite them as "wiki-design decision NNNN"). It uses the runbooks but does not edit `wiki-design/`. **First use on a fresh checkout:** run `softhier_vla_wiki/tools/wiki.py setup` once (venv + deps + index + hook; downloads the embedding model). Afterwards run the tool by path, no activation needed: `softhier_vla_wiki/tools/wiki.py find "…"` (it re-execs into `.venv`). Read this file first; paths in commands are wiki-relative (`knowledge/x.md`). Commits go into the submodule (`softhier_vla_wiki/tools/wiki.py commit …`); the parent then shows the submodule as modified — bumping its pointer is the user's call.

## Setup
```bash
tools/wiki.py setup   # venv + deps + index + commit hook; first run downloads the embedding model (~130 MB)
```
`.venv/` and `.index/` are git-ignored; `.index/` is a rebuildable cache (`rm -rf .index && tools/wiki.py index`). Each folder's summary files are `_abstract.md` and `_overview.md` (`cat <dir>/_abstract.md`); write only their body, `stamp` manages the `covers:` frontmatter.
