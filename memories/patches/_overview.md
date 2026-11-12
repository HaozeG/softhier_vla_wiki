# memories/patches/

A log of the changes SoftHier-VLA made to upstream infrastructure, one note (type `patch`) per upstream repository or branch.

**Rules** ([status and patch logs](../../wiki-design/decisions/2026-11-12-status-and-patch-logs.md)):
- **The code repository is canonical.** Patch files, apply order and rationale (commit messages) stay there (for GVSoC: `infra/softhier/gvsoc-patches/`). A wiki entry holds only what the code repository lacks: upstream status, measured impact, and links.
- **Keyed by finding ID** (F-id, such as F13: the project's numbering of a finding in the design document's findings table), not by patch number. A patch series is re-exported and renumbered; the finding ID stays. The patch column names the number as of a stated code-repository commit.
- **Labelled and sourced.** Every row's measured-impact cell carries a label (`measured`, `estimate` or `inference`, as the [glossary](../../glossary/evidence.md) defines them) and every row links to commit-pinned permalinks.
- **Superseded, not deleted.** When a patch is dropped, merged upstream or replaced, set its status to `superseded` (or `upstreamed`) with a link to what replaced it, and keep the row.
- **Upstream status** says only what a record shows: "no upstream PR recorded" until a pull request exists, then its link.

**Catalog**
- [GVSoC soft_hier_release patches](gvsoc-soft-hier-release.md) — the ten patches on upstream `d806a84`, by finding: what each changes, upstream status, measured impact.
