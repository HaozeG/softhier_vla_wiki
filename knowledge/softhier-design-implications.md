---
type: concept
tags: [softhier, design, implications, mapping, quantization, serving]
sources: [resources/compression/efficientvla.md, resources/compression/clp-layer-pruning.md, resources/compression/lightvla.md, resources/compression/dysl-vla.md, resources/compression/deer-vla.md, resources/compression/vla-cache.md, resources/compression/pruned-vla-recovery.md, resources/compression/quantvla.md, resources/compression/bitvla.md, resources/models/openvla.md, resources/models/openvla-oft.md, resources/models/tinyvla.md, resources/models/octo.md, resources/models/pi0.md, resources/models/pi05.md, resources/models/rt-2.md, resources/models/fast-tokenizer.md, resources/models/gr00t-n1.md, resources/models/smolvla.md, resources/serving/vla-perf.md, resources/serving/vla-xpu-characterization.md, resources/serving/vla-edge-bottleneck-characterization.md, resources/serving/jetson-pi.md, resources/serving/flashvla-streaming.md, resources/serving/real-time-chunking.md, resources/serving/realtime-vla.md, resources/serving/vla-cpp.md, resources/serving/vla-simd.md, resources/serving/embodied-cpp.md, resources/serving/litevla-edge.md, resources/surveys/survey-embodied-fm-edge.md]
---
# Implications of the sources for SoftHier-VLA

## Summary
This note collects what the ingested sources mean for our project: designing a VLA serving mapping for SoftHier. The source notes in `resources/` only record what each source says; the reading for SoftHier-VLA is done here, grouped by design question. Five conclusions carry most of the weight: (1) the action-expert loop and decode phases are memory-bound, so memory-first optimization is the safer default; (2) run-time control flow (dynamic depth, learned token counts) conflicts with statically scheduled tile mappings unless padded or bucketed; (3) weight-only low-bit quantization gains little without a native low-bit datapath; (4) the action head should stay at higher precision than the language model; (5) no source measures a flow-matching VLA on a 10 TOPS-class device, so any budget there is an estimate.
## Diagram
```text
Source finding                     Design question it feeds
---------------------------------  ----------------------------------
phase timings, roofline, Jetson    where is time spent?  -> memory-first
  and XPU measurements                                      mapping
token pruning, caching, dynamic    run-time control flow  -> static tile
  depth, static pruning               vs fixed shapes          schedules
quantization results               datapath and precision -> low-bit
                                                              support?
async, chunk stitching, streaming  serving schedule       -> latency
                                                              hiding
model recipes and sizes            reference workload     -> SmolVLA-class
```

## Details
**Where the time goes (mapping priorities)**
- Weight-bound devices gain more from parameter reduction than compute-rich GPUs (Thor 2.23× vs H100 1.16× at the same pruning ratio), which supports memory-first optimization for edge targets; the action head is a fixed latency floor ([pruned-VLA recovery](../resources/compression/pruned-vla-recovery.md)).
- On LPDDR-class edge devices, token-by-token generation is bandwidth-bound and added TOPS help little ([edge bottleneck study](../resources/serving/vla-edge-bottleneck-characterization.md)). That study concerns reasoning VLAs with many decode tokens; for chunked flow-matching VLAs the analogous phase is the action-expert loop ([VLA-Perf](../resources/serving/vla-perf.md)).
- VLA-Perf is the best public model for where a VLA is bound; its memory-bound action expert and bandwidth-limited edge GPU feed [inference workload characterization](inference-workload-characterization.md). It models only Thor-class edge devices and assumes BF16, so nothing near 10 TOPS is evaluated.
- The XPU study is the only source with a 10 TFLOP/s-class accelerator (Ascend 310B); it confirms the compute-bound VLM / memory-bound expert split on real devices ([XPU study](../resources/serving/vla-xpu-characterization.md), [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md)).
- Jetson-PI's action-expert time (536.8 of 1420.8 ms) shows the flow loop as a major cost on bandwidth-limited devices ([Jetson-PI](../resources/serving/jetson-pi.md)).
- EfficientVLA's memory-bound saturation result is the central caution for token-pruning claims: FLOP savings do not translate to latency once the device is bandwidth-bound; its per-module time and FLOP split is a template for our own workload analysis ([EfficientVLA](../resources/compression/efficientvla.md), measured on an A40 GPU, not an edge device).
- Autoregressive action decoding is dominated by memory-bound decode passes over the full LLM ([FAST](../resources/models/fast-tokenizer.md)); π0.5 adds a variable-length text decode before its flow loop ([π0.5](../resources/models/pi05.md)). The biggest lever for a 7B VLA is removing sequential decode passes rather than FLOPs ([OpenVLA-OFT](../resources/models/openvla-oft.md)), and a decode-free action head, not only a smaller LLM, drives the latency win ([TinyVLA](../resources/models/tinyvla.md)).
- On a GPU, launch and synchronization overhead is about 4× between naive and tuned execution. The per-GEMM shape list of π0 in [Realtime-VLA](../resources/serving/realtime-vla.md) is the set of shapes a many-PE mapping must schedule; VLA-Perf's roofline is validated against it.

**Static schedules versus run-time control flow**
- Learned token counts ([LightVLA](../resources/compression/lightvla.md)) imply variable sequence lengths at run time, which conflicts with static tile schedules unless padded or bucketed.
- Dynamic depth costs efficiency on real hardware: DeeR-VLA reaches 68% wall-clock saving against an 81% FLOP reduction, which matters for a statically scheduled many-PE mapping ([DeeR-VLA](../resources/compression/deer-vla.md)). DeeR uses an LSTM head, so it does not directly apply to SmolVLA-style experts.
- DySL-VLA's finding that per-layer controllers add serial latency is a caution for dynamic schemes on statically scheduled hardware; the mapping must honour run-time control flow ([DySL-VLA](../resources/compression/dysl-vla.md)).
- Static compression is the hardware-friendly alternative: CLP removes layers before fine-tuning, so it changes the deployed model, not the run-time control flow ([CLP](../resources/compression/clp-layer-pruning.md)). See [layer skipping and pruning](layer-skipping-and-pruning.md).
- VLA-Cache maps to a hardware-friendly "partial prefill" but requires storing per-layer KV for the previous frame ([VLA-Cache](../resources/compression/vla-cache.md)). See [token pruning and caching](token-pruning-and-caching.md).

**Precision and datapath**
- BitVLA is the only work here that directly motivates custom low-bit datapaths: a ternary×INT8 multiply-accumulate needs no multipliers. Its latency gain depends on a specialised kernel; on a generic accelerator without ternary support the benefit would be memory only ([BitVLA](../resources/compression/bitvla.md)).
- Weight-only quantization brings small speedups (1.08–1.14×) unless there is a native low-bit datapath, and discrete preprocessing (index precision) must be validated ([vla.cpp](../resources/serving/vla-cpp.md)).
- OpenVLA's int8-vs-int4 result warns that weight quantization only helps when the kernel is memory-bound and dequantization is cheap ([OpenVLA](../resources/models/openvla.md)).
- The flow/diffusion action head, run for many steps and accumulating error across them, is the most quantization-sensitive part, so a mixed-precision plan (LLM 4-bit weights, action head at higher precision or MLP-only) is the safer default ([QuantVLA](../resources/compression/quantvla.md)). 4-bit hurt π0.5 (0.70 relative success) while GR00T N1.7 held (0.96) ([embodied.cpp](../resources/serving/embodied-cpp.md)). See [quantization](quantization.md).

**Serving schedule**
- RTC is the reference algorithm for hiding latency when a chunk takes longer than the control period, which is the regime an edge accelerator will be in. Its extra backpropagation through the action expert adds compute (76 → 97 ms in the paper's setup), which an accelerator must support ([RTC](../resources/serving/real-time-chunking.md)).
- FlashVLA amortizes the flow loop across control steps (a scheduling change, not a smaller model), turning the memory-bound expert into a steady pipeline; it was only tested on GPUs from RTX A4000 upward ([FlashVLA](../resources/serving/flashvla-streaming.md)).
- vla.simd's action-supply view shows a slow query can still sustain control if the chunk is long enough ([vla.simd](../resources/serving/vla-simd.md)).
- embodied.cpp confirms the runtime pattern (C++ graphs, fused batch-1 execution, plugin heads) that vla.cpp and Jetson-PI use. See [serving methods](serving-methods.md).
- The shared failure modes on the RK3588 (fragmented graphs, shared-DRAM contention, throttling) are a checklist, not device evidence ([embodied foundation models at the edge](../resources/surveys/survey-embodied-fm-edge.md), [RK3588 deployment](rk3588-vla-deployment.md)).

**Reference workloads and targets**
- SmolVLA is the reference small VLA: its layer counts, token counts, expert size and 10 flow steps give the inputs for the [edge budget estimate](edge-budget-estimate.md); its layer skipping motivates layer pruning and its async stack is a serving method ([SmolVLA](../resources/models/smolvla.md)).
- GR00T N1 is a second data point for the efficient recipe (middle-layer VLM features, 64 tokens per frame, few-step flow); its dual-system split is analysed in [serving methods](serving-methods.md) ([GR00T N1](../resources/models/gr00t-n1.md)).
- Octo (27–93M parameters, cheap diffusion head) is a viable lower bound on compute, with weaker semantic generalization ([Octo](../resources/models/octo.md)).
- π0's latency table is the most cited first-party breakdown (vision, prefill, 10-step action loop); at 3.3B parameters it is above the size of a 10 TOPS-class deployment ([π0](../resources/models/pi0.md)).
- RT-2 marks the first generation of VLA serving: cloud inference at low Hz, the origin of the discrete-token action design ([RT-2](../resources/models/rt-2.md)).
- vla.cpp is the most useful public data for sub-Thor devices (SmolVLA on an 8 GB Orin Nano, CPU-only latencies); vla.simd gives the lowest-compute measured point (8.2 s per 50-action chunk on a Pi 5 CPU). LiteVLA-Edge is only a feasibility anecdote: no task success, unclear device ([LiteVLA-Edge](../resources/serving/litevla-edge.md)).

**How the surveys are used**
- Yu et al. is the taxonomy backbone for [VLA efficiency taxonomy](vla-efficiency-taxonomy.md); Guan et al. cross-checks it. The two overlap heavily, so cite primary papers for any number. Guan's claim that most latency sits in the LLM is refined by VLA-Perf, which shows the action expert dominating on Jetson Thor for π0.
- Ma et al. is the terminology reference for [VLA architecture overview](vla-architecture-overview.md); it predates most efficiency and edge work.
- Zhong et al. frames why workloads differ: raw-action VLAs (π0, SmolVLA, OpenVLA) are our target, whereas language-plan and reasoning tokens add long decode phases. See [action representation and chunking](action-representation-and-chunking.md).

## Open questions
- No flow-matching VLA is measured on a 10 TOPS-class part; every budget there extrapolates ([edge budget estimate](edge-budget-estimate.md)).
- No source measures dynamic-depth or token-pruning schemes on statically scheduled many-PE hardware, so their wall-clock cost there is unknown.
