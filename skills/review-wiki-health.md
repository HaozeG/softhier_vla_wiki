---
type: runbook
tags: [lint, maintenance]
sources: []
---
# Review wiki health

Run periodically (weekly, or after a large ingest), by hand or via the `wiki-health` subagent.

## Steps
1. `tools/wiki.py health` — read the whole report.
2. **Errors first** (`ERROR` rows fail `check`): fix `MISSING`/`EMPTY`/`STALE`/`TOO LONG` summary files, `UNCATALOGUED` notes, `FRONTMATTER`/`BADTYPE`/`NOTITLE`/`NOSECTION` structure, `BROKENLINK`s, `DIAGRAM` (diagram wider than 80 columns or not plain ASCII); `TABLEFMT` warnings are cleared by `tools/wiki.py fmt`.
3. **`NEARDUP` / `DUPLICATE`:** read both notes fully. Merge into the stronger note — the one with more sources/detail, else the older, better-named one (union the `tags:` and `sources:`, redirect inbound links, remove its catalog line, delete the weaker one) or, if they are legitimately different, cross-link them and state the difference in each.
4. **`ORPHAN`:** run `tools/wiki.py related <note>` and link it from the notes that should point to it (a catalog entry in `_overview.md` does not count as a link). If nothing related exists yet, leave it as a deliberate warning.
5. **`PLACEHOLDER` / `NOSOURCES` / `NOTAGS`:** resolve from the actual source or report that information is missing; never invent.
6. **Contradictions:** `tools/wiki.py health --candidates` lists related-but-distinct pairs (`REVIEW`, similarity 0.65 to the duplicate threshold). Read each pair for conflicting claims or stale statements; fix the wrong note, or record the tension in both and cross-link.
7. **Stale claims:** for notes that a recent ingest should have affected, `tools/wiki.py log --pages` shows what changed and when; check whether older notes still assert what newer sources supersede, and update them.
8. **Missing pages:** a concept, component or term that keeps appearing across notes (`tools/wiki.py find "<term>" -n 10`, `grep -rl`) but has no note of its own deserves one (`new concept|entity …`).
9. **Diagram vs text:** for each note with a diagram, check that every box and arrow has a supporting sentence, every sentence about structure appears in the diagram, numbers agree, and decision trees cover all cases without gaps ([decision 0007](../memories/decisions/0007-ascii-diagrams-as-logic-check.md)). Fix the stale side; list notes with structure but no diagram. Redraw rather than patch when the logic changed.
10. **Data gaps:** collect `## Open questions` sections and unanswered `Relevance` items; list them for the user as suggested next sources.
11. `tools/wiki.py stamp` → `index` → `health` until only deliberate warnings remain. Staleness cascades: after changing a directory's abstract, `check` flags parents up to the root; review them and `stamp .`.
12. **Log:** when asked to commit: `tools/wiki.py commit lint "<subject>"`.

## Troubleshooting
- Threshold too noisy or too quiet: `tools/wiki.py health --dup-threshold 0.90` (noisier) or `0.95`. The default 0.93 was calibrated in [decision 0005](../memories/decisions/0005-near-duplicate-threshold.md); lower it temporarily with `--candidates` to look for overlap that is not a copy.
- Index looks wrong: `rm -rf .index && tools/wiki.py index`.

New content goes in via the [ingest runbook](ingest-a-source.md); the rationale for these checks is [decision 0002](../memories/decisions/0002-lint-and-git-as-log.md).
