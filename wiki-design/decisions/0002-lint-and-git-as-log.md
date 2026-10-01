---
type: decision
tags: [wiki, lint, git, maintenance]
sources: [https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f]
---
# 0002: Typed notes, health lint, and git as the change log

## Context
An LLM-maintained wiki compounds only if it stays consistent: notes must share a structure,
duplicates must not accumulate, and there must be a trustworthy record of what changed when.
Karpathy's "LLM wiki" pattern uses raw sources, an LLM-owned wiki, and a schema file, with
ingest / query / lint operations and a chronological log. This wiki maps those onto its own tools.
Mapping to the gist (read and checked): raw sources → `resources/` + raw files; wiki → `knowledge/`, `memories/`, `skills/`; schema → `CLAUDE.md`; index.md → L1 `.overview.md` catalog; log.md → git commits with trailers. Deliberate divergence: dates live in git, not in frontmatter or a log file.

## Decision
- **Typed notes.** Every note has frontmatter (`type`, `tags`, `sources`), a `# Title`, and the
  `##` sections required by its type (see `tools/wiki.py` `TYPES`). `wiki.py new` scaffolds them.
- **Catalog = L1 sidecars.** A note must be linked, with a one-line summary, from its directory's `.overview.md` (Karpathy's index.md role).
- **Lint = `wiki.py health`.** Structural checks plus zvec near-duplicate detection; run by the `wiki-health` subagent.
- **Git is the log** (Karpathy's log.md role). No dates in files. Each operation is one commit
  `wiki(<op>): <subject>` with `Date:`/`Op:`/`Pages:`/`Sources:` trailers; `wiki.py log` reads them back.
- **zvec is the relational layer.** `find` (hybrid), `related` (nearest neighbours + "not linked yet"),
  `health` (near-duplicates) answer questions `ls`/`grep` can't: what is similar, what should be linked, what overlaps.

## Why
- Dates in files drift and duplicate git; trailers are greppable and versioned with the change.
- Failing fast on structure keeps notes machine-readable, so retrieval and summaries stay reliable.
- Cross-linking on ingest (via `related`) is where the compounding value comes from.

Builds on [0001](0001-wiki-layout-and-search.md); procedures: [ingest](../runbooks/ingest-a-source.md), [health review](../runbooks/review-wiki-health.md).

Followed by [0003 Claude Code plugin](0003-claude-code-plugin.md).

Note: the file names and the word "sidecar" used here were replaced by [0006](0006-rename-folder-summary-files-and-plain-language.md).
