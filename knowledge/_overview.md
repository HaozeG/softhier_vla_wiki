---
covers: e80618f603d3
---
# knowledge/

Synthesis of what the sources say about physical AI; VLA models are the first covered area (further areas get their own notes), with a focus on how they are built, made efficient and served on robot hardware. Each note cites `resources/` notes. Start order: the README, the glossary (`../glossary/_overview.md`), then the two notes below.

- [One VLA call, step by step](one-vla-call.md) — start here: plain-language walkthrough of one call, with one picture
- [VLA edge serving overview](vla-edge-serving-overview.md) — next: findings, reading path, trust guide
- [SoftHier and the project](softhier-and-the-project.md) — what the project README says: mapping VLA applications to a tile-based many-PE chip; goals
- [VLA architecture overview](vla-architecture-overview.md) — components, action heads, reference models
- [Action representation and chunking](action-representation-and-chunking.md) — tokens vs regression vs flow; chunk size
- [SmolVLA](smolvla.md) — the reference small VLA and its measured latencies
- [Inference workload characterization](inference-workload-characterization.md) — phases, roofline vs measured, overheads
- [Serving methods](serving-methods.md) — async, chunk stitching, dual-system, runtimes, placement
- [Layer skipping and pruning](layer-skipping-and-pruning.md) — static, dynamic and width pruning
- [Token pruning and caching](token-pruning-and-caching.md) — visual token reduction and reuse
- [Quantization for VLAs](quantization.md) — INT4, ternary, W4A8, and where they help
- [Flow-step reduction](flow-step-reduction.md) — fewer steps, caching, streaming
- [Technique comparison](technique-comparison.md) — speedup, accuracy cost, hardware per technique
- [Edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md) — device classes; no VLA measured at 10 TOPS
- [RK3588 deployment](rk3588-vla-deployment.md) — practices and evidence on the common robot board
- [Robot compute partitioning](robot-compute-partitioning.md) — Unitree/AgiBot controller vs AI tiers, published rates, what runs on RK3588
- [VLA efficiency taxonomy](vla-efficiency-taxonomy.md) — survey categories mapped to notes; naming pitfalls
