# Wiki conventions (read before editing)

An LLM-maintained wiki for SoftHier-VLA. You (the agent) own the wiki: you write and maintain it, the human curates sources and asks questions. The point is **compounding**: knowledge is synthesized once into linked, structured notes and kept current, not re-derived from raw sources on every question.

## Architecture
| Layer | Where | Rule |
|---|---|---|
| Sources | raw files (PDFs, data) you are given; `resources/` holds one faithful note per source | Raw files are immutable: read, never modify. Source notes: correct errors, don't editorialize |
| Wiki | `knowledge/` (synthesis), `memories/decisions/` (decisions), `skills/` (runbooks) | You maintain it; every note cross-linked and cited |
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
Required `##` sections: concept/entity → `Summary`; paper → `Summary`, `Key claims`; decision → `Context`, `Decision`, `Why`; runbook → `Steps`; comparison → `Summary`, `Comparison` (a table; use for analysed questions such as design trade-offs). Scaffold with `tools/wiki.py new <type> <path> "<Title>"`. Rules: one topic per note; claim first; short paragraphs/lists; relative links to related notes; no dates in files (git records them); no `TODO` left behind; never invent facts — cite `sources:`; use plain words over jargon, and define any unavoidable term the first time it appears ([decision 0006](memories/decisions/0006-rename-folder-summary-files-and-plain-language.md)).

**Diagrams ([decision 0007](memories/decisions/0007-ascii-diagrams-as-logic-check.md)).** A note whose content has structure (pipeline, timeline, tiers, decision tree, taxonomy, dataflow) carries one ```` ```text ```` ASCII diagram, usually right after `## Summary`: plain ASCII, ≤80 columns, ~25 lines, no line starting with `#`. The diagram adds no claim and no number the text lacks; text and diagram change in the same edit. Drawing it is a second check on the prose: if a case is missing, an arrow contradicts a sentence, or quantities do not add up, fix the text from the cited source and say so in the commit body. Not for tables of numbers, `resources/` notes, or `_abstract.md`/`_overview.md`.

## The three operations
- **Ingest** a source → follow `skills/ingest-a-source.md`. First tell the user the key takeaways and what you plan to touch. One source touches several notes (often 10–15): source note, the knowledge notes it informs, cross-links, catalog entries, decisions.
- **Query** → `find "<question>"` (hybrid semantic + keyword), `ls`/`tree` to browse, read L0/L1 then the L2 hits. Answer from the wiki and cite `wiki://` URIs. If the answer is a valuable synthesis, **file it back** as a note (a good answer that stays in chat is lost).
- **Lint** → `tools/wiki.py health` (or the `wiki-health` subagent); procedure in `skills/review-wiki-health.md`. Covers duplicates, contradictions, stale claims superseded by newer sources, orphans, concepts that deserve their own page, and data gaps. Run after large ingests and periodically.

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
| `check [--strict]` | Fast structural lint, no model: folder summary files (missing, empty, stale, too long), frontmatter, sections, links, catalog, diagrams (`DIAGRAM`: over 80 columns or non-ASCII), unfilled template comments, orphans, TODOs, exact duplicates |
| `health [--strict] [--dup-threshold 0.93] [--candidates]` | `index` + `check` + zvec near-duplicate detection; `--candidates` also lists related-but-distinct pairs to read for contradictions |
| `stamp [<dirs>]` | Record the folder's content hash in its summary files after you rewrite them |
| `commit <op> "<subject>" [--source URL]... [--body ...] [--dry-run]` | Lint-gated commit with structured message |
| `log [-n N] [--op OP] [--path P] [--pages]` / `history <note>` | Read the change log back from git |
| `setup` | One-time: create `.venv`, install deps, build the index, enable the hook (works from any cwd, e.g. `softhier_vla_wiki/tools/wiki.py setup`) |
| `install-hooks` | Enable the `commit-msg` hook that enforces the format below |

## Write workflow (every insert / update / delete)
1. Edit notes. Update the directory's `_overview.md` (catalog line) and `_abstract.md` if its summary changed; parents too.
2. `stamp <dirs>` → `check`. Staleness cascades upward: a directory's hash includes its children's L0 abstracts, so changing `knowledge/_abstract.md` flags the root summary files too; review them and stamp (`stamp .` for root). Re-stamping an accurate sidecar is fine. Replace placeholder text such as "Empty until populated" when adding the first note.
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

- **Wiki-development session** (started in this repo): improves the schema/tooling, runs `wiki-health`, curates structure. The `wiki-health` subagent (`.claude/agents/`) is discoverable only from here.
- **Working session in the parent repo** (this repo is its `softhier_vla_wiki/` submodule): queries the wiki and files updates while doing other work (e.g. design plans). **First use on a fresh checkout:** run `softhier_vla_wiki/tools/wiki.py setup` once (venv + deps + index + hook; downloads the embedding model). Afterwards run the tool by path, no activation needed: `softhier_vla_wiki/tools/wiki.py find "…"` (it re-execs into `.venv`). Read this file first; paths in commands are wiki-relative (`knowledge/x.md`). Commits go into the submodule (`softhier_vla_wiki/tools/wiki.py commit …`); the parent then shows the submodule as modified — bumping its pointer is the user's call.

## Setup
```bash
tools/wiki.py setup   # venv + deps + index + commit hook; first run downloads the embedding model (~130 MB)
```
`.venv/` and `.index/` are git-ignored; `.index/` is a rebuildable cache (`rm -rf .index && tools/wiki.py index`). Each folder's summary files are `_abstract.md` and `_overview.md` (`cat <dir>/_abstract.md`); write only their body, `stamp` manages the `covers:` frontmatter.
