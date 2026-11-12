# memories/

Project memory: what was decided and learned while working on SoftHier-VLA.

- `decisions/` — project decision records (`YYYY-MM-DD-slug.md`: context, decision, why). They record choices, not results: numbers produced by experiments do not go here.
- `status/` — project status log: one entry per theme of work, in sequence, with a current-state paragraph at the top of its overview.
- `patches/` — log of changes made to upstream infrastructure (such as GVSoC), keyed by finding ID: upstream status, measured impact and links; the patch files themselves stay in the code repository.

**Derived content.** Elsewhere in the wiki notes state only what sources say ([wiki-design decision 0013](../wiki-design/decisions/0013-scope-and-no-derived-content.md)). `status/` and `patches/` are the exception: they may hold the project's own measurements, estimates and inferences, with every claim labelled `measured`, `estimate` or `inference`, linked to its source (a commit-pinned permalink into the code repository, or a wiki note), and marked superseded rather than deleted when outdated ([status and patch logs](../wiki-design/decisions/2026-11-12-status-and-patch-logs.md)). `check` enforces the labels and links (note types `status` and `patch`).

Other memory types (entities, cases) are added when there is content for them.
