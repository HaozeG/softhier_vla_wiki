---
type: decision
tags: [ingest, workflow, reading, learning]
sources: [session:ingest-vla-workload-characterization]
defines: []
---
# 0015: Ingest starts by choosing brainstorming or in-depth mode

## Context
The ingest runbook ran one way only. The agent read the whole source, extracted the claims and wrote the notes, then told the maintainer the takeaways. That is fast and suits sources the maintainer only needs filed. But for a source the project builds on, such as the paper chosen as the starting point for benchmarking, the maintainer wants to understand the source themselves. An automatic summary leaves them with the notes but without having read the paper. They asked to be offered a choice at the start of every ingest: let the agent do it automatically, or be led through the source while reading it side by side.

## Decision
Every ingest begins by asking the maintainer which mode to use ([runbook](../runbooks/ingest-a-source.md), step 0).

```text
            new source
                |
        ask: which mode?
         /              \
  brainstorming        in-depth
  agent reads all,     agent reads all, gives a reading map,
  extracts, writes     then per section (one per turn):
  notes, reports       point to section -> maintainer reads ->
         \             check question -> terms -> draft claims
          \            -> maintainer corrects        (x sections)
           \              /
      synthesis, glossary, diagram, cross-links, catalog, verify
```

- **Brainstorming** (automatic): the existing flow. The agent reads the whole source, files the source note and the knowledge notes, then reports the takeaways and a few check questions.
- **In-depth** (guided reading): the maintainer opens the source beside the session. The agent first reads the whole source and gives a reading map: sections in order, what each contributes, which to skim. Then it goes one section per turn. Each turn names where to read (section, page, figure or table) and two or three things to look for. After the maintainer reads, it asks one check question (predict-then-read or explain-back) and explains any new terms, using the glossary first. It then drafts that section's key claims and the maintainer corrects them. The agent waits before the next section. Shared synthesis runs after the last section.
- The maintainer can switch modes at any point ("faster" finishes the rest automatically; "slow down" switches to guided reading).
- Both modes produce the same wiki output and follow the same rules (project-neutral source notes, no derived content per [0013](0013-scope-and-no-derived-content.md)). The maintainer's own questions and working conclusions from a reading session go to session memory, not the wiki, unless the source states them.
- **Exception: critique of the source.** Where the maintainer asks for it, points the source leaves unclear, argues weakly or assumes without saying go into a `## Reading notes (inference)` section at the end of the source note, before `## Related`. The section is labelled as the readers' inference, stays project-neutral (no SoftHier-VLA discussion, [0010](0010-resources-stay-project-neutral.md)) and is the only editorial part of a source note. This is the explicit request that [0013](0013-scope-and-no-derived-content.md) requires for inferences.

## Why
- The two modes serve different goals: filing a source versus learning it. Asking takes one question, and guessing wrong costs either the maintainer's understanding or their time.
- Reading one section per turn, with a question before moving on, matches how the maintainer prefers to learn (predict-then-check, confirm understanding before the next stage).
- Drafting claims per section, with the maintainer correcting them, gives a second check on the source note beside the agent's own reading.
- Revisit if most ingests end up in one mode. The question could then default to that mode and be skipped unless asked.
