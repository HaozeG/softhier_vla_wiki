---
type: decision
tags: [schema, formatting, obsidian, tables]
sources: [memories/decisions/0007-ascii-diagrams-as-logic-check.md, session:obsidian-tables]
---
# 0008: Write tables padded the way Obsidian does

## Context
The maintainer reads the wiki in Obsidian. Opening a note there rewrites its markdown tables (every column padded to equal width, separator row `| ---- |` sized to match), which shows up as unwanted changes in git. Compact tables (`|---|---|`) written by agents therefore keep producing diffs.

## Decision
- Every pipe table is stored in Obsidian's padded form: one space inside each pipe, every cell padded to its column's widest cell (counted in characters, minimum 3), separator row filled with dashes to the same width, alignment colons kept.
- `tools/wiki.py fmt` rewrites all notes into that form (idempotent, whitespace only); `fmt --check` only reports. `check` warns `TABLEFMT` for any unpadded table. The formatter was verified to reproduce Obsidian's own output on a table Obsidian had reformatted.
- Run `fmt` after editing tables, before `stamp`. Tables whose rows have unequal cell counts are left alone and reported.

## Why
Matching the viewer's format removes a source of noise commits and keeps real changes visible in `git diff`. Padding makes raw tables a little wider in the editor, which is the cost of the rule.

Builds on [0007](0007-ascii-diagrams-as-logic-check.md).
