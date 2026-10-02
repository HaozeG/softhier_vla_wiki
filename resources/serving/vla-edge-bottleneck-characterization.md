---
type: paper
tags: [characterization, jetson-orin, jetson-thor, memory-bound, molmoact, recent]
sources: [arxiv:2603.02271, https://arxiv.org/abs/2603.02271]
---
# Characterizing VLA Models: Identifying the Action Generation Bottleneck for Edge AI Architectures

Vishwanathan, Subramanian, Raghunathan (Google, Purdue), arXiv 2603.02271 (Mar 2026). A three-page extended abstract; details are sparse.

## Summary
Profiles MolmoAct-7B (an action-reasoning VLA that autoregressively generates reasoning tokens and waypoints) on Jetson AGX Orin (64 GB) and Jetson Thor (128 GB), then projects scaled models up to 100B parameters on hypothetical memory systems (GDDR7, processing-in-memory) with an in-house simulator. Its central claim is that the memory-bound generation phase, not the vision encoder or the action transformer, dominates latency for reasoning-style VLAs.

## Key claims
- **Measured (Fig. 2):** up to about 75% of end-to-end latency is the autoregressive generation phase; latencies are about 200–300× above what 10 Hz control needs; Thor has 5× the compute of Orin but only 1.4× lower end-to-end latency, because generation is bandwidth-bound.
- **Hardware assumed (Table 1):** Orin LPDDR5 203 GB/s with 100 BF16 TFLOPS; Thor LPDDR5X 273 GB/s with 500 BF16 TFLOPS; hypothetical Orin+GDDR7 1000 GB/s, Thor+PIM 2180 GB/s with 3993 TFLOPS.
- **Projection (Fig. 3):** GDDR7 and PIM raise control frequency but still fall well below the 10–20 Hz target at 10–100B parameters; the authors call for algorithm-system co-design.
- **Method caveats:** the simulator is validated at 70–90% accuracy against production accelerators (their statement); the profiled model is a discrete-token reasoning VLA, unlike the flow-matching action experts in π0/SmolVLA. Peak-throughput figures differ by 2× or more between papers (see [VLA XPU characterization](vla-xpu-characterization.md)).

## Related
See also: [VLA-Perf](vla-perf.md), [XPU study](vla-xpu-characterization.md), [Jetson specs](../hardware/nvidia-jetson-platform-specs.md).
