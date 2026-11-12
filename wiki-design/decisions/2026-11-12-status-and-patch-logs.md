---
type: decision
tags: [scope, schema, inference, evidence, status, patches, lint]
sources: [wiki-design/decisions/0013-scope-and-no-derived-content.md, wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md, session:wiki-status-patches]
defines: []
---
# Labelled derived content allowed in two logs: project status and upstream patches

## Context
[Decision 0013](0013-scope-and-no-derived-content.md) keeps derived estimates, inferences and design implications out of the wiki unless the user asks, because such notes went stale and a reader could not tell a source's measurement from our extrapolation. The project now produces its own results (simulated runs, success-rate evaluations, fixes to upstream simulators), and the maintainer wants two records of them in the wiki: a log of where the project stands, and a log of the changes made to upstream infrastructure. Both hold figures the project computed itself, some of them composed from partial runs, which 0013 would exclude. The project's code repository already keeps the full records (design documents, run logs, patch files), so the wiki entries only need to summarise and point to them.

Alternatives considered: keep these logs only in the code repository and in session memory (the earlier practice: numbers in the experiment's results file with a memory pointer); or lift 0013 for all of `memories/`. The first leaves the wiki without a project timeline; the second reopens the problem 0013 fixed.

## Decision
```text
+--------------------------------------------------------------------------+
| resources/, knowledge/, glossary/, memories/decisions/                   |
| 0013 unchanged: what sources say; derived content only on request        |
+--------------------------------------------------------------------------+
+--------------------------------------------------------------------------+
| memories/status/   (type status)    memories/patches/   (type patch)     |
| derived content allowed, each claim labelled measured|estimate|inference |
| and linked to its source in the code repo (commit-pinned)                |
| outdated entries or rows marked superseded, never deleted                |
+--------------------------------------------------------------------------+
        ^ summarises and links to
+--------------------------------------------------------------------------+
| code repository: design docs, run logs, patch files (canonical)          |
+--------------------------------------------------------------------------+
```
- **Two areas only.** `memories/status/` (project status log) and `memories/patches/` (log of changes to upstream infrastructure) may hold derived content: the project's own measurements, estimates and inferences. Everywhere else 0013 applies unchanged.
- **Evidence label on every claim.** Each claim states one label: `measured` (a run, with how it was run, for example "simulated on GVSoC, ideal HBM"), `estimate` (a figure computed from specs, configs or partial runs, not run as a whole) or `inference` (our reasoning, not checked by a run). The labels are the glossary's ([evidence](../../glossary/evidence.md)).
- **Source on every claim.** Each claim links to where it is recorded: a file in the code repository as a commit-pinned permalink (`https://github.com/<owner>/<repo>/blob/<full commit>/<path>`), or a wiki note. A claim with no record is not written.
- **Superseded, not deleted.** When an entry or row is outdated, it stays and is marked superseded, with a link to what replaced it (`superseded_by:` for status entries, a status column for patch rows). The history stays readable and git gives the dates.
- **Status entries** are titled by theme, never by date or pull-request number. The order of the catalog in `memories/status/_overview.md` gives the sequence, frontmatter `follows:` and `superseded_by:` link neighbours, and the overview opens with a current-state paragraph. Rules in that overview.
- **Patch entries** are keyed by the project's finding ID, not by patch number, since a patch series is re-exported and renumbered. The canonical patch files stay in the code repository; the wiki holds only what they lack: upstream status, measured impact and links. Rules in `memories/patches/_overview.md`.
- **Lint.** Two note types, `status` and `patch`, each allowed only in its folder (and the only types allowed there). `check` requires the frontmatter `evidence:` list (labels used in the note) and `sources:`, a `Label` column whose cells are labels, a `Source` column with a link in every row, and resolving `follows:` / `superseded_by:` targets; patch rows also need a finding ID.
- **0013 itself** gets a one-line "revised by" pointer to this decision, not a rewrite. The places that restate 0013 (`CLAUDE.md`, `README.md`, `memories/_overview.md`, the plugin skill, the runbooks) name the two exceptions.

## Why
A project timeline and a patch log are useful to later sessions only if they sit next to the knowledge and decisions they refer to. 0013's reason still holds: derived figures go stale and can pass for sourced ones. The rules above answer it: a label on every claim keeps a reader from mistaking an estimate for a measurement, a commit-pinned link lets the claim be checked against the record it came from, superseding instead of deleting shows when a claim stopped being current, and confining the content to two folders keeps the rest of the wiki under 0013.

Revisit if status or patch entries start to repeat what the code repository records in full (then shorten them to links), or if derived content appears outside the two folders.

Builds on [0004](0004-evidence-tiers-for-fast-moving-vla-sources.md), [0013](0013-scope-and-no-derived-content.md) and [0014](0014-note-writing-style.md).
