---
type: concept
tags: [overview, vla, edge, serving, start-here]
sources: [resources/surveys/survey-efficient-vla-yu.md, resources/surveys/survey-efficient-vla-guan.md, resources/serving/vla-perf.md, resources/models/smolvla.md, resources/models/pi0.md, resources/serving/vla-cpp.md, resources/serving/jetson-pi.md]
---
# VLA edge serving: overview and reading list

## Summary
A vision-language-action (VLA) model is a program that turns a robot's camera images and a written instruction into the commands that move its arms. How fast a robot can run one is limited by how long one call takes on the chip inside the robot, because the model must read a lot of data from memory and do a lot of arithmetic before it answers. This wiki found that current small models, together with executing queued commands while the next call runs, can keep a robot moving, but that almost nothing is measured on small chips of about ten trillion operations per second (10 TOPS) or less.

## Findings in brief
**The problem:** a robot needs the next batch of commands from the model before the last batch runs out, and one call can take longer than a batch lasts. **The approaches:** make one call cheaper (smaller models, fewer layers, tokens, steps or bits, better software) and hide the delay by queueing a chunk of actions while the next call runs. **The trade-offs:** most savings cost some accuracy or need retraining, and some only pay off with the right low-level kernels. **What is open:** how the techniques combine, and how fast a small chip runs a flow-matching VLA, since almost nothing is measured there. The sourced findings follow.

- **Models got smaller.** Early VLAs ([RT-2](../glossary/evaluation-and-models.md), up to 55B parameters and served from the cloud, and [OpenVLA](../glossary/evaluation-and-models.md)) ran at 1–6 Hz (see [Hz](../glossary/symbols-and-conventions.md)) on cloud or workstation GPUs. Current efficient designs ([SmolVLA](../glossary/evaluation-and-models.md), [GR00T N1](../glossary/evaluation-and-models.md), [π0](../glossary/evaluation-and-models.md)) have fewer parameters, emit chunks of actions from a small flow-matching expert and hide latency with asynchronous execution. (B means billions of parameters, the learned numbers of a model.)
- **Where the time goes depends on the model and the device.** A call has three parts: reading the images and text (a lot of arithmetic in the π0-class models profiled), an expert that re-reads its weights at every step (limited by memory speed), and software overhead that can be larger than both. VLA-Perf's roofline model (a lower bound on time from a chip's arithmetic and memory speeds) puts the expert behind memory and the image and text reading behind arithmetic on the GPUs it models; a measured GPU profile in the XPU study has the expert taking about twice as long as the vision-language model. The [workload note](inference-workload-characterization.md) reports both without reconciling them.
- **On a small board the sources report little.** One self-reported community result says a small VLA took about 5 seconds per chunk on a Rockchip RK3588 board (about 6 TOPS), and its README says this is longer than the chunk lasts, so the action queue runs empty. No measured flow-matching VLA exists for a device of about 10 TOPS; the sources offer proxies instead.

Devices that appear in the sources ([glossary: devices](../glossary/devices-and-toolchains.md)):
- [Jetson Orin and Thor](../glossary/devices-and-toolchains.md): NVIDIA embedded GPU modules, where almost all measured edge results come from.
- [RK3588](../glossary/devices-and-toolchains.md): a Rockchip chip with an NPU; the one self-reported SmolVLA result.
- [Ascend 310B](../glossary/devices-and-toolchains.md): a Huawei accelerator of about ten TFLOP/s; one plot shows [ACT](../glossary/model-and-attention.md) (a small action-chunk policy) at about 10 Hz on it, and no bar for a flow-matching VLA.
- CPU runs (Raspberry Pi 5, desktop CPUs) and the Jetson Orin Nano: the other proxies.

## Details
**Read in this order** (reading steps; the calls inside one VLA call have their own numbers in that note). Keep the [glossary](../glossary/_overview.md) open for new words ([A to Z index](../glossary/a-to-z.md)). Reading steps 4 and 5 can be read in either order, the four notes of step 9 in any order, and step 12 any time after step 8.
1. [README](../README.md): what the wiki covers and where to start. You will know what the topic is and what the project is ([SoftHier and the project](softhier-and-the-project.md)).
2. [One VLA call, step by step](one-vla-call.md): you will be able to describe one call from camera images to a chunk of actions.
3. This overview: you will know the main findings and which note holds each.
4. [VLA architecture overview](vla-architecture-overview.md): you will know the parts of a VLA and how designs differ.
5. [Action representation and chunking](action-representation-and-chunking.md): you will know the three ways a VLA produces actions and why it returns chunks.
6. [SmolVLA](smolvla.md): you will be able to follow one small model through its sizes and the speeds reported for it.
7. [Inference workload characterization](inference-workload-characterization.md): you will know the phases of a call and what limits each.
8. [Serving methods](serving-methods.md): you will know how the sources hide latency: asynchronous execution, chunk stitching, dual systems and placement.
9. Optimization notes: [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [quantization](quantization.md), [flow-step reduction](flow-step-reduction.md). You will know what each technique acts on and what the sources report for it.
10. [Technique comparison](technique-comparison.md): you will have one table of the reported effect of each technique.
11. Hardware view: [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md); optional deep dives: the most common robot board in [RK3588 deployment](rk3588-vla-deployment.md) and [robot compute partitioning](robot-compute-partitioning.md). You will know what is measured on which device and which compute tier commercial robots give to control and to AI.
12. [VLA efficiency taxonomy](vla-efficiency-taxonomy.md): you will see how the surveys group the literature.

**Source names used in these notes** (one line each; the notes are in `resources/`)
- [VLA-Perf](../resources/serving/vla-perf.md): a roofline latency model for VLAs on a device, an edge server or the cloud.
- [XPU study](../resources/serving/vla-xpu-characterization.md): a benchmark of VLAs on GPUs, NPUs and CPUs ranked by cost, energy and time.
- [vla.cpp](../resources/serving/vla-cpp.md): a C++ runtime for eleven VLAs with latencies across many devices.
- [vla.simd](../resources/serving/vla-simd.md): a CPU inference engine and an analysis of how many actions per second a slow policy supplies.
- [Jetson-PI](../resources/serving/jetson-pi.md): a system stack and a future-state predictor for asynchronous π0.5 serving on Jetson boards.
- [FlashVLA](../resources/serving/flashvla-streaming.md): streaming action decoding that advances several chunks in each pass.
- [RTC](../resources/serving/real-time-chunking.md): real-time chunking, which stitches a late chunk to the actions already committed.
- VLASH: a method that uses the robot's future state for asynchronous execution; the sources discuss it but this wiki has no note on it.

**Best-supported findings**
- VLA-Perf's roofline model puts the action expert (few tokens, weights re-read each step) behind memory and prefill and vision behind arithmetic, except on bandwidth-poor Jetson Thor where all three phases are memory-bound; a measured profile in the XPU study has the expert taking about twice the vision-language model's time ([VLA-Perf](../resources/serving/vla-perf.md), [VLA XPU characterization](../resources/serving/vla-xpu-characterization.md); see [workload note](inference-workload-characterization.md)).
- Naive software is 4–9× off the roofline; graph capture, fused kernels and fixed shapes recover most of it ([Realtime-VLA](../resources/serving/realtime-vla.md), [Jetson-PI](../resources/serving/jetson-pi.md)).
- Redundant depth is real: 30–50% of layers can be removed from π0, GR00T-N1.5 and SmolVLA with small loss when fine-tuned ([CLP](../resources/compression/clp-layer-pruning.md)); heavier weight pruning needs distillation recovery.
- Chunking plus async execution lets a slow model keep a robot moving: vla.simd gives conditions on latency against chunk duration for continuous supply, and real-time chunking, Jetson-PI and FlashVLA address late chunks ([serving methods](serving-methods.md)).
- Quantization saves memory reliably; speed gains need native low-bit kernels ([quantization](quantization.md)).

**Least-supported areas**
- Real-robot evidence is small and benchmark results are mostly LIBERO simulation with a single seed.
- Many strongest efficiency results come from papers posted within the last months and not independently reproduced (tagged `recent`).
- Energy and power are almost never measured; sub-20-TOPS accelerators have no tabulated flow-VLA measurements.

**How to trust a number here:** check the hardware, precision, baseline (eager vs tuned) and whether it is a roofline estimate or a measurement. Vendor TOPS figures are sparse INT8/FP4 headline numbers, not dense BF16 ([edge hardware](edge-hardware-and-the-10-tops-gap.md)).

## Open questions
- What a ~10 TOPS NPU actually achieves on a flow-matching VLA (operator support, utilization, bandwidth).
- How the compute of SmolVLA splits between its vision path and its LLM half: not reported (the π0-class split in the workload note is not transferred).
- Whether small models keep enough generalization after truncation, pruning and quantization combined.
