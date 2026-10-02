---
type: glossary
tags: [glossary, benchmarks, evidence]
sources: [wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md, resources/models/smolvla.md]
---
# Evaluation and models

## Summary
Benchmark names and the evidence tags on source notes. The tag meanings are the wiki's own convention and are loaded into project sessions. Model descriptions are in the [catalog of model notes](../resources/models/_overview.md), not here.

## Terms
| Term               | Meaning                                                                        | Scope      | Defined in                                                                                               |
| ------------------ | ------------------------------------------------------------------------------ | ---------- | -------------------------------------------------------------------------------------------------------- |
| LIBERO, Meta-World | Simulated robot-manipulation benchmarks.                                       | field      | [SmolVLA](../knowledge/smolvla.md)                                                                       |
| SO100, SO101       | Low-cost real robot arms used for real-world tests.                            | field      | [SmolVLA](../knowledge/smolvla.md)                                                                       |
| success rate       | Share of benchmark episodes in which the task is completed.                    | field      | [SmolVLA](../knowledge/smolvla.md)                                                                       |
| tag recent         | A source posted within a few months of ingest or not independently reproduced. | convention | [wiki-design decision 0004](../wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md) |
| tag low-evidence   | A source with latency-only claims, unclear devices or no task success.         | convention | [wiki-design decision 0004](../wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md) |
| tag first-party    | A vendor or company page: marketing-level unless numbers are given.            | convention | [wiki-design decision 0004](../wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md) |
| tag community      | A forum post or community repository.                                          | convention | [wiki-design decision 0004](../wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md) |
