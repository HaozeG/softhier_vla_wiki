---
type: glossary
tags: [glossary, project]
sources: [wiki-design/decisions/0012-glossary-with-on-demand-lookup.md, session:parent-readme, https://github.com/gvsoc/gvsoc/tree/soft_hier_release]
---
# Project terms

## Summary
Terms that SoftHier-VLA defines in its own design decisions, such as the name of a mapping or a schedule. Their names are listed at the start of every project session, and they override general knowledge. A decision that introduces or redefines a term lists it in `defines:` and adds its row here in the same commit. The row SoftHier comes from the project README (see the SoftHier SDK page); other rows come from decisions.

## Terms
| Term             | Meaning                                                                                                                                                                                                                     | Scope   | Defined in                                                                                             |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------ |
| SoftHier         | The tile-based many-PE chip that this project maps VLA applications to.                                                                                                                                                     | project | [SoftHier and the project](../knowledge/softhier-and-the-project.md)                                   |
| golden reference | A small program, independent of the compiler flow, that runs the original model in full precision on a fixed observation and records its intermediate tensors in a fixed layout; simulator results are compared against it. | project | [First baseline decision](../memories/decisions/2026-11-10-first-baseline-latency-and-success-rate.md) |
