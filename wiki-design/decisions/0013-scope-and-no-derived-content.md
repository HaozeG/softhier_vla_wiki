---
type: decision
tags: [scope, schema, sources, inference]
sources: [session:scope-and-no-derived-content]
---
# 0013: Scope is physical AI; notes state what sources say, not derived content

## Context
The wiki began as the knowledge base for one question, how VLA models run on a small chip. Over time `knowledge/` also gained content that no source states: an arithmetic estimate of a SmolVLA call on a 10-TOPS device, a note of design implications for SoftHier-VLA, "rules of thumb", "choosing a method" mappings and hypotheses. It was written before any rule governed it and was never reviewed, and it can mislead a later reader, who cannot tell a source's measurement from our extrapolation. What the project needs from the wiki is a clear and complete statement of what each concept and technique is, what it acts on and how the parts relate, so that later, more advanced discussions of techniques and their combinations stand on a solid base.

## Decision
```text
+----------------------------------------------------------------------------+
| resources/   what one source says, with its evidence tier                  |
+----------------------------------------------------------------------------+
        |  cited by
        v
+----------------------------------------------------------------------------+
| knowledge/   what each concept is, what it acts on, how the parts relate;  |
| every claim sourced; a source's own estimate stays, labelled as its        |
+----------------------------------------------------------------------------+
        : only if the user asks; labelled `inference`; outside routine upkeep
        v
+----------------------------------------------------------------------------+
| derived estimates, solution proposals, design implications                 |
+----------------------------------------------------------------------------+
```
- **Scope:** physical AI, meaning robots that perceive and act in the physical world. The first area covered is vision-language-action (VLA) models: how they are built, made efficient and run on robot hardware. Folders and note names do not change; further areas get their own notes.
- **Notes state what the sources say and how things relate.** No derived estimates, solution proposals, design implications or inferences are written in routine work. If the user asks for one, it is labelled `inference` and kept out of routine upkeep. An estimate made by a source stays and is labelled as the source's ([0004](0004-evidence-tiers-for-fast-moving-vla-sources.md)).
- **Accurate numbers are not required** for a concept to be clear. Notes keep the few sourced figures that help, phrased as approximate where natural, and add no computed values of their own.
- **Removed in this change:** `knowledge/edge-budget-estimate.md` and `knowledge/softhier-design-implications.md`, with their links and catalog lines; the RK3588 estimate, utilization and hypothesis passages; the "implications", "inferences" and "choosing a method" sections and the "rules of thumb" that were our own judgement in the workload, serving, robot-compute, token-pruning, quantization, flow-step and action-representation notes. `knowledge/softhier-and-the-project.md` restates only what the project README says about the project and SoftHier.

## Why
The value of the wiki is a reliable, complete base for later discussion. Derived content mixes our guesses with what sources report, goes stale as soon as a source changes, and was never checked. Keeping only what sources say makes every claim traceable, and a user who wants an estimate or a proposal can ask for it knowingly.

Builds on [0004](0004-evidence-tiers-for-fast-moving-vla-sources.md), [0009](0009-separate-project-knowledge-from-wiki-design.md) and [0010](0010-resources-stay-project-neutral.md).
