---
type: decision
tags: [workflow, tooling, lint, commits, memory]
sources: [session:workflow-trim]
defines: []
---
# Trim workflow steps that cost time without catching errors

## Context
A review of one long session (an ingest, an in-depth reading, then commit, merge and push) found that much of the time went to bookkeeping rather than content:

| Cost                                                                      | Cause                                                                                                          |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Re-stamping summary files up to the root after every edit                 | the `covers` hash of each folder included its children's abstracts, so one changed note flagged every ancestor |
| Merge conflicts in six summary files                                      | concurrent branches each re-stamped `covers:` lines and re-listed folder contents in abstracts                 |
| A hand-made `.venv` symlink in every worktree, removed before each commit | `wiki.py` looked for the venv only inside the worktree; `.venv/` in `.gitignore` does not match a symlink      |
| Renumbering a decision in five files                                      | two sessions took the same next number                                                                         |

## Decision
- **No `covers` hash, no `stamp`.** `check` warns `STALE` once for a folder whose notes changed since the last commit while neither of its summary files did. It does not cascade to parents; a parent's summary changes only when its scope changes.
- **Summary files describe scope, not contents.** `_abstract.md` says what the folder is for; it does not list children or carry counts. The `_overview.md` catalog lines are the one listing.
- **Worktrees share the main checkout's venv.** `wiki.py` falls back to it; `.gitignore` entries have no trailing slash.
- **New decisions are named `YYYY-MM-DD-<slug>.md`**, so concurrent sessions cannot collide. Existing numbered decisions keep their names and are still cited by number. A decision may be revised in place when a later one changes it; the later one says what it replaced.

## Why
Each removed step either repeated what git already records (which files changed, and when) or produced merge conflicts without catching a real error. The checks that catch errors (catalog lines, links, sections, glossary) stay.
