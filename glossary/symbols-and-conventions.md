---
type: glossary
tags: [glossary, notation]
sources: [resources/serving/vla-simd.md, resources/serving/jetson-pi.md]
---
# Symbols and conventions

## Summary
The symbols that recur across the notes and where the wiki uses one letter for two things. Every row is a convention and is loaded into project sessions.

## Terms
| Term           | Meaning                                                                                                                | Scope      | Defined in                                                                                            |
| -------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
| H, n, K        | Actions per chunk: the same quantity under different names in different sources.                                       | convention | [action representation and chunking](../knowledge/action-representation-and-chunking.md)              |
| T              | Number of flow steps per chunk.                                                                                        | convention | [flow-step reduction](../knowledge/flow-step-reduction.md)                                            |
| l (ℓ)          | Latency of one model call.                                                                                             | convention | [serving methods](../knowledge/serving-methods.md)                                                    |
| dt (Δt)        | Control period.                                                                                                        | convention | [serving methods](../knowledge/serving-methods.md)                                                    |
| g              | Fraction of a chunk left in the queue at which the next call is requested.                                             | convention | [serving methods](../knowledge/serving-methods.md)                                                    |
| L              | LLM layer count in model notes; in the Jetson-PI part of the serving note, actions executed per chunk. Check the note. | convention | [serving methods](../knowledge/serving-methods.md)                                                    |
| N              | Number of LLM layers used.                                                                                             | convention | [SmolVLA](../knowledge/smolvla.md)                                                                    |
| xN in diagrams | A loop that repeats N times.                                                                                           | convention | [wiki-design decision 0011](../wiki-design/decisions/0011-diagrams-show-parts-data-and-repetition.md) |
