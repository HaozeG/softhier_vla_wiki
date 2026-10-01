---
type: decision
tags: [schema, diagrams, quality, ascii]
sources: [memories/decisions/0002-lint-and-git-as-log.md, session:ascii-diagrams]
---
# 0007: Draw an ASCII diagram for structural notes, and use it to check the text

## Context
The maintainer prefers that concepts be shown as plain-text diagrams, for two reasons: a diagram lets a person or an agent grasp a structure at a glance, and drawing it is a second check on the prose. If the logic cannot be drawn, or the drawing disagrees with the sentences, one of them is wrong. A first pass over the `knowledge/` notes found real problems this way: a summary that contradicted its own table (RK3588 one-camera case), a summary naming a role the body says is disputed, two latency conditions merged into one, a three-way latency choice described as two-way, an overview line that contradicted the serving note, and a table mixing chunk rate with actions per second.

## Decision
Notes whose content has structure get one ASCII diagram, usually right after the `## Summary`.
- **Use for:** pipelines, timelines, tiers or layers, decision trees, taxonomies, dataflow, small budgets. **Skip for:** plain fact lists and tables of numbers (a table is already the right picture); one diagram per note is normal, more only if the note covers separate structures.
- **Format:** a fenced block tagged `text`, at most 80 columns and about 25 lines, plain ASCII only (`+ - | > v ^ [ ] ( )`, no box-drawing glyphs or emoji). Never start a diagram line with `#` (it looks like a heading to readers and tools). Follow a diagram with one line saying how to read it only if it is not self-evident.
- **The diagram adds no claims.** Every box and arrow must match a sentence in the same note; the sentence carries the citation. Numbers appear in a diagram only if they appear in the text, because a number in two places can drift.
- **Same edit, both places.** When the text changes, change the diagram in the same edit, and the other way round.
- **Draw it as a check.** While drawing, ask: do the cases cover all inputs, do the arrows follow the text, do the quantities add up? If not, fix the text from the cited `resources/` note, and say what changed in the commit message body.
- **Not in** `_abstract.md` / `_overview.md` (size limits) or `resources/` notes (they stay faithful to their source).

`check` enforces the format: a `DIAGRAM` error for lines wider than 80 columns or containing non-ASCII characters. Where it is written down: `CLAUDE.md` note rules and its `check` row, the `concept`, `entity` and `comparison` templates (a guidance comment, which `check` makes you fill or delete), the ingest and health-review runbooks, and the plugin skill.

## Why
Prose can hide a gap that a picture exposes (a missing branch, two steps that cannot both be true). The rule costs little because the diagram only restates what the text already says. Limits keep diagrams readable in a terminal, an editor and an embedding index. Tooling note: `find`/`index` embed diagram lines as ordinary text; the chunker was changed to ignore `#` inside fenced blocks, and `health` after adding diagrams to 16 notes reported no near-duplicates, so no threshold change was needed.

Builds on [0002](0002-lint-and-git-as-log.md).

See also [0008](0008-obsidian-padded-tables.md): tables are stored padded like Obsidian.
