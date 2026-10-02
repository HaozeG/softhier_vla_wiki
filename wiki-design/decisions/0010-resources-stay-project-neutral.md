---
type: decision
tags: [schema, layout, resources, knowledge]
sources: [wiki-design/decisions/0009-separate-project-knowledge-from-wiki-design.md, session:resources-project-neutral]
---
# 0010: Keep `resources/` project-neutral; put project discussion in `knowledge/`

## Context
Every paper-type source note carried a `## Relevance to SoftHier-VLA` section (35 notes) with design readings, such as "conflicts with static tile schedules", and links into `knowledge/`. That mixed two jobs: recording what a source says, and deciding what it means for us. The second changes as the design changes, so the source notes kept needing edits for reasons unrelated to the source, and the project reading was scattered over 35 files.

## Decision
```text
resources/<topic>/       what the source says (summary, claims, caveats)
        |                no SoftHier-VLA discussion, no links to knowledge/
        v  cited by
knowledge/               what the sources mean for SoftHier-VLA
        |                (incl. softhier-design-implications.md)
        v  informs
memories/decisions/      what we chose
```
- A `resources/` note holds only the source's own content: `Summary`, `Key claims` (with section, figure or table refs), and its scope caveats (device, precision, evidence tier). It may link to other `resources/` notes under `## Related`.
- It contains no "relevance", "implications" or "for us" text and no links into `knowledge/`; links run one way, from `knowledge/` to `resources/`.
- The `paper` template's `## Relevance to SoftHier-VLA` section is replaced by an optional `## Related`.
- Project readings of sources live in `knowledge/`; `knowledge/softhier-design-implications.md` collects the design implications per question, citing the source notes.
- The health review checks the separation with `grep` (runbook step 10).

## Why
Source notes stay stable and reusable (they change only when the source or its reading is wrong), while the project reading lives in one place that is revised as the design evolves. The one-way link direction also lets `knowledge/` be rewritten without touching `resources/`.

Builds on [0009](0009-separate-project-knowledge-from-wiki-design.md) and [0004](0004-evidence-tiers-for-fast-moving-vla-sources.md).
