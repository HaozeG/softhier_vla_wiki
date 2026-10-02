---
type: concept
tags: [overview, vla, edge, serving, start-here]
sources: [resources/surveys/survey-efficient-vla-yu.md, resources/surveys/survey-efficient-vla-guan.md, resources/serving/vla-perf.md, resources/models/smolvla.md, resources/models/pi0.md, resources/serving/vla-cpp.md, resources/serving/jetson-pi.md]
---
# VLA edge serving: overview and reading path

## Summary
A vision-language-action (VLA) model is a program that turns a robot's camera images and a written instruction into the commands that move its arms. How fast a robot can run one is limited by how long one call takes on the chip inside the robot, because the model must read a lot of data from memory and do a lot of arithmetic before it answers. This wiki found that current small models, together with executing queued commands while the next call runs, can keep a robot moving, but that almost nothing is measured on chips of about ten trillion operations per second (10 TOPS) that this project targets.

## Findings in brief
- **Models got smaller.** Early VLAs ([RT-2](../glossary/evaluation-and-models.md), up to 55B and served from the cloud, and [OpenVLA](../glossary/evaluation-and-models.md)) had 7–55 billion parameters (B, the learned numbers of a model) and ran at 1–6 Hz (see [Hz](../glossary/symbols-and-conventions.md)) on cloud or workstation GPUs. Current efficient designs ([SmolVLA](../glossary/evaluation-and-models.md), [GR00T N1](../glossary/evaluation-and-models.md), [π0](../glossary/evaluation-and-models.md)) have 0.45–3B parameters, emit chunks of actions from a small flow-matching expert and hide latency with asynchronous execution.
- **Serving cost has three parts:** vision plus prefill (compute-bound), an iterative expert (memory-bound), and software overhead that can dwarf both ([memory-bound versus compute-bound](../glossary/hardware-and-performance.md)).
- **Measured edge results** almost all use [Jetson Orin and Thor](../glossary/hardware-and-performance.md), NVIDIA's embedded GPU modules. **For a ~10 TOPS device there is no measured flow-matching VLA beyond one self-reported result on an [RK3588](../glossary/hardware-and-performance.md) board (SmolVLA about 5 s per chunk); the sources otherwise offer CPU and Orin Nano proxies, and one plot with [ACT](../glossary/model-and-attention.md) (a small action-chunk policy) at about 10 Hz on an [Ascend 310B](../glossary/hardware-and-performance.md) accelerator.**

## Diagram
```text
Reading path (numbers match "Read in this order")
+----------------------------------------------------------------------------+
| 0 README -> 1 glossary -> 2 one VLA call -> 3 this overview                |
+----------------------------------------------------------------------------+
     v
+----------------------------------------------------------------------------+
| 4 architecture, 5 action representation (either order) -> 6 SmolVLA        |
+----------------------------------------------------------------------------+
     v
+----------------------------------------------------------------------------+
| 7 inference workload -> 8 serving methods                                  |
+----------------------------------------------------------------------------+
     v
+----------------------------------------------------------------------------+
| 9 layer skipping, token pruning, quantization, flow steps -> 10 comparison |
+----------------------------------------------------------------------------+
     v
+----------------------------------------------------------------------------+
| 11 hardware (edge devices, RK3588, robot compute)                          |
+----------------------------------------------------------------------------+
12 taxonomy (map of the literature): read any time after 8
```

## Details
**Read in this order** (new to the field? start at 0; steps 4 and 5 can be read in either order, the four notes of step 9 in any order, and step 12 any time after 8)
0. [README](../README.md): what the wiki is and how to use it; [SoftHier and the project](softhier-and-the-project.md) says what this project is about.
1. The [glossary](../glossary/_overview.md): plain-words definitions of the terms used below, in groups: [robot and control loop](../glossary/robot-and-control-loop.md), [model and attention](../glossary/model-and-attention.md), [action generation](../glossary/action-generation.md), [hardware and performance](../glossary/hardware-and-performance.md) (memory-bound versus compute-bound), [compression](../glossary/compression.md), [evaluation and models](../glossary/evaluation-and-models.md), [symbols and conventions](../glossary/symbols-and-conventions.md), [project terms](../glossary/project-terms.md).
2. [One VLA call, step by step](one-vla-call.md): the whole story of one call in plain language, with one picture.
3. This overview.
4. [VLA architecture overview](vla-architecture-overview.md): what a VLA is and how designs differ.
5. [Action representation and chunking](action-representation-and-chunking.md): tokens vs regression vs flow; why chunks.
6. [SmolVLA](smolvla.md): the reference small model and its serving numbers across sources.
7. [Inference workload characterization](inference-workload-characterization.md): where time goes; roofline vs measured.
8. [Serving methods](serving-methods.md): async, chunk stitching, dual-system, runtimes, placement.
9. Optimization notes: [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [quantization](quantization.md), [flow-step reduction](flow-step-reduction.md).
10. [Technique comparison](technique-comparison.md): the summary table of speedup, accuracy cost and hardware per technique.
11. Hardware view: [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md), the most common robot board in [RK3588 deployment](rk3588-vla-deployment.md), and which compute tier commercial robots give to control and to AI in [robot compute partitioning](robot-compute-partitioning.md).
12. Map of the literature: [VLA efficiency taxonomy](vla-efficiency-taxonomy.md).

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
