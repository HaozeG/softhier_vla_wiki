---
covers: c45d89957e58
---
# knowledge/

Synthesis of what the sources say about physical AI; VLA models are the first covered area (further areas get their own notes), with a focus on how they are built. Each note cites `resources/` notes. Start with the frame notes below (SoftHier, VLA, WAM), with the glossary (`../glossary/_overview.md`) open for new words.

## Frame

- [SoftHier and the project](softhier-and-the-project.md) — what the project README says: mapping VLA applications to a tile-based many-PE chip; goals
- [One VLA call, step by step](one-vla-call.md) — start here: plain-language walkthrough of one call, with one picture
- [VLA architecture overview](vla-architecture-overview.md) — components, action heads, reference models
- [World action models (WAM)](wam-overview.md) — definition, taxonomy and cost model from one survey; other WAM definitions open

## Reference

- [Action representation and chunking](action-representation-and-chunking.md) — tokens vs regression vs flow; chunk size
- [SmolVLA](smolvla.md) — the reference small VLA, its data flow and sizes
- [Dual-system VLA](dual-system-vla.md) — System 1 and System 2 as separate networks at different rates; contrast with SmolVLA
- [Fast policy trained by RL](fast-policy-trained-by-rl.md) — RL Token, Real-Time EXPO-FT and π*0.6: where RL enters a VLA
- [Low-level policy loop](low-level-policy-loop.md) — a 50 Hz one-action-per-call joint policy (microduck): inputs, tick, CPU vs NPU, camera placement
