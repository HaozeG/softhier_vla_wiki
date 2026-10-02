---
type: concept
tags: [overview, vla, edge, serving, start-here]
sources: [resources/surveys/survey-efficient-vla-yu.md, resources/surveys/survey-efficient-vla-guan.md, resources/serving/vla-perf.md, resources/models/smolvla.md, resources/models/pi0.md, resources/serving/vla-cpp.md, resources/serving/jetson-pi.md]
---
# VLA edge serving: overview and reading path

## Summary
Vision-language-action (VLA) models drive robots from images and instructions. Early VLAs (RT-2, OpenVLA) were 7–55B and ran at 1–6 Hz on cloud or workstation GPUs; current efficient designs (SmolVLA, GR00T N1, π0) are 0.45–3B, emit chunks of actions from a small flow-matching expert, and hide latency with asynchronous execution. Serving cost has three parts: vision plus prefill (compute-bound), an iterative expert (memory-bound), and software overhead that can dwarf both. Measured edge results almost all use Jetson Orin/Thor; **for a ~10 TOPS device there is no measured flow-matching VLA beyond one self-reported RK3588 community result (SmolVLA about 5 s per chunk); the sources otherwise offer estimates, CPU and Orin Nano proxies, and one plot with ACT (not a VLM) at about 10 Hz on an Ascend 310B.**

## Diagram
```text
Reading path (numbers match "Read in this order")

+--------------------------+
| 0 concepts first (terms) |
+--------------------------+
        |
        v
+------------------+    +-------------------------+    +------------------+
| 1 architecture   |--->| 2 action representation |--->| 3 SmolVLA        |
+------------------+    +-------------------------+    +------------------+
                                                               |
                                                               v
                         +--------------------+    +----------------------+
                         | 5 serving methods  |<---| 4 inference workload |
                         +--------------------+    +----------------------+
                                    |
                                    v
+------------------------------------------------------------------------------+
| 6 optimization: layer skipping, token pruning, quantization, flow steps      |
| (summary table: technique comparison)                                        |
+------------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------------+
| 7 hardware: edge hardware and 10 TOPS gap -> edge budget estimate            |
| RK3588 deployment, robot compute partitioning                                |
+------------------------------------------------------------------------------+

8 taxonomy: maps survey categories onto notes 5 and 6
```
Serving cost, per the Summary: vision + prefill (compute-bound), expert loop (memory-bound), software overhead on top.

## Details
**Read in this order** (new to the field? start with 0)
0. [Concepts first](concepts-first.md): plain-words definitions of the terms used below, with a worked memory-bound example.
1. [VLA architecture overview](vla-architecture-overview.md): what a VLA is and how designs differ.
2. [Action representation and chunking](action-representation-and-chunking.md): tokens vs regression vs flow; why chunks.
3. [SmolVLA](smolvla.md): the reference small model and its serving numbers across sources.
4. [Inference workload characterization](inference-workload-characterization.md): where time goes; roofline vs measured.
5. [Serving methods](serving-methods.md): async, chunk stitching, dual-system, runtimes, placement.
6. Optimization notes: [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [quantization](quantization.md), [flow-step reduction](flow-step-reduction.md); summary table in [technique comparison](technique-comparison.md).
7. Hardware view: [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md), the arithmetic in [edge budget estimate](edge-budget-estimate.md), the most common robot board in [RK3588 deployment](rk3588-vla-deployment.md), and which compute tier commercial robots give to control and to AI in [robot compute partitioning](robot-compute-partitioning.md).
8. Map of the literature: [VLA efficiency taxonomy](vla-efficiency-taxonomy.md).

**Best-supported findings**
- The action expert (few tokens, weights re-read each step) is memory-bound on every device tested; prefill and vision are compute-bound except on bandwidth-poor Jetson Thor ([VLA-Perf](../resources/serving/vla-perf.md), [VLA XPU characterization](../resources/serving/vla-xpu-characterization.md)).
- Naive software is 4–9× off the roofline; graph capture, fused kernels and fixed shapes recover most of it ([Realtime-VLA](../resources/serving/realtime-vla.md), [Jetson-PI](../resources/serving/jetson-pi.md)).
- Redundant depth is real: 30–50% of layers can be removed from π0, GR00T-N1.5 and SmolVLA with small loss when fine-tuned ([CLP](../resources/compression/clp-layer-pruning.md)); heavier weight pruning needs distillation recovery.
- Chunking plus async execution lets a slow model keep a robot moving if latency is below the chunk duration; RTC-style stitching helps when latency exceeds the control period so chunks arrive late, and above the chunk duration only a smaller model or a dual-system split helps ([serving methods](serving-methods.md)).
- Quantization saves memory reliably; speed gains need native low-bit kernels ([quantization](quantization.md)).

**Least-supported areas**
- Real-robot evidence is small and benchmark results are mostly LIBERO simulation with a single seed.
- Many strongest efficiency results come from papers posted within the last months and not independently reproduced (tagged `recent`).
- Energy and power are almost never measured; sub-20-TOPS accelerators have no tabulated flow-VLA measurements.

**How to trust a number here:** check the hardware, precision, baseline (eager vs tuned) and whether it is a roofline estimate or a measurement. Vendor TOPS figures are sparse INT8/FP4 headline numbers, not dense BF16 ([edge hardware](edge-hardware-and-the-10-tops-gap.md)).

## Open questions
- What a ~10 TOPS NPU actually achieves on a flow-matching VLA (operator support, utilization, bandwidth).
- Whether small models keep enough generalization after truncation, pruning and quantization combined.
