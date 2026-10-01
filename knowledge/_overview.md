---
covers: 206f19b880d1
---
# knowledge/

Synthesis for VLA serving on edge hardware, each note citing `resources/` notes. Start with the overview.

- [VLA edge serving overview](vla-edge-serving-overview.md) — start here: findings, reading path, trust guide
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
- [Edge budget estimate](edge-budget-estimate.md) — SmolVLA arithmetic for a 10-TOPS device (estimate)
- [RK3588 deployment](rk3588-vla-deployment.md) — practices and evidence on the common robot board; SmolVLA estimate
- [Robot compute partitioning](robot-compute-partitioning.md) — Unitree/AgiBot controller vs AI tiers, published rates, what runs on RK3588
- [VLA efficiency taxonomy](vla-efficiency-taxonomy.md) — survey categories mapped to notes; naming pitfalls
