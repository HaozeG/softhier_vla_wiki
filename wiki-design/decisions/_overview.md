---
covers: f3dd93a4c8ed
---
# wiki-design/decisions/

- [0001 wiki layout and search](0001-wiki-layout-and-search.md) — layered L0/L1/L2 directory summaries (from OpenViking) plus local hybrid search with zvec + fastembed; no server or API keys.
- [0002 typed notes, lint, git as the log](0002-lint-and-git-as-log.md) — typed notes with required sections, `health` lint with zvec near-duplicate detection, git commits with trailers as the dated change log.
- [0003 Claude Code plugin for parent-repo sessions](0003-claude-code-plugin.md) — SessionStart hook + `wiki` skill, local-scope install, no doc mandate.
- [0004 evidence tiers for fast-moving VLA sources](0004-evidence-tiers-for-fast-moving-vla-sources.md) — read primary text, tag recent/low-evidence/first-party/community, record caveats beside claims.
- [0005 near-duplicate threshold 0.93](0005-near-duplicate-threshold.md) — raised from 0.82 after calibration on a single-topic corpus; copies still flagged.
- [0006 rename folder summary files, plain language](0006-rename-folder-summary-files-and-plain-language.md) — `_abstract.md`/`_overview.md` replace the dot-file "sidecars"; plain words over jargon.
- [0007 ASCII diagrams as a logic check](0007-ascii-diagrams-as-logic-check.md) — structural notes carry one plain-text diagram that must match the prose; drawing it is a second check on the text.
- [0008 Obsidian-padded tables](0008-obsidian-padded-tables.md) — tables stored padded like Obsidian so opening notes there causes no diffs; `wiki.py fmt` and a `TABLEFMT` warning enforce it.
- [0009 separate project knowledge from wiki design](0009-separate-project-knowledge-from-wiki-design.md) — project content and wiki design in separate folders, following OpenViking's resource / memory / skill split; resources grouped by topic.
- [0010 resources stay project-neutral](0010-resources-stay-project-neutral.md) — source notes record what a source says; what it means for SoftHier-VLA lives in `knowledge/`, links run one way.
- [0011 diagrams show parts, data and repetition](0011-diagrams-show-parts-data-and-repetition.md) — a diagram must answer: what are the parts, what data passes between them and how big, what repeats; built with `tools/diagram.py`, box alignment linted.
- [0012 glossary loaded by the plugin](0012-glossary-loaded-by-the-plugin.md) — grouped glossary with field, convention and project scopes; convention and project terms are injected at session start; a decision defining a term adds its row.
