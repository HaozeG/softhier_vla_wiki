---
type: concept
tags: [workload, roofline, memory-bound, prefill, action-expert, latency-breakdown]
sources: [resources/serving/vla-perf.md, resources/serving/realtime-vla.md, resources/serving/vla-xpu-characterization.md, resources/serving/vla-edge-bottleneck-characterization.md, resources/serving/vla-cpp.md, resources/serving/jetson-pi.md, resources/models/pi0.md, resources/models/openvla-oft.md, resources/models/fast-tokenizer.md, resources/compression/efficientvla.md]
---
# Inference workload characterization

## Summary
(Unfamiliar terms such as memory-bound are explained in [glossary: hardware and performance](../glossary/hardware-and-performance.md).)

A flow-matching VLA call has three phases: vision encoding and VLM prefill (large matrix multiplies over hundreds of tokens, compute-bound on GPUs) and an iterative action-expert loop (few tokens, weights re-read every step, memory-bound). On bandwidth-poor edge devices all three can become memory-bound. Measured latencies sit several times above the roofline unless launch and synchronization overheads are engineered away; autoregressive-action VLAs replace the expert loop with a decode-dominated phase.

## Diagram
```text
ONE FLOW-MATCHING CALL (pi0-class, 3 cameras, 800 prefix tokens)

  3 camera images
        |  256 tokens per image
        v
+--------------------------------+
| 1 VISION ENCODER               |    compute-bound on GPUs, 321 FLOP/byte
+--------------------------------+
        | visual tokens + text + state
        | = 800 tokens in total
        v
+--------------------------------+
| 2 VLM PREFILL                  |    compute-bound on GPUs, 543 FLOP/byte
+--------------------------------+
        | prefix keys + values, kept
        | for all T steps
        v
+--------------------------------+
| 3 ACTION EXPERT                |<--+
| few tokens per step            |   |  repeats T times (T = 4-10)
|                                |---+  memory-bound: weights re-read
+--------------------------------+      every step, 54 FLOP/byte
        |
        v  chunk of actions

On Jetson Thor all three phases are memory-bound. Autoregressive-action VLAs
replace phase 3 with token-by-token decode through the full LLM (OpenVLA 7
tokens, pi0-FAST 30-60 tokens).
```

**In plain words.** Every phase of a call needs arithmetic and memory reads, and whichever takes longer sets that phase's time. A phase's *intensity* is its arithmetic per byte read (FLOP/byte); a chip's *balance point* is its arithmetic speed divided by its memory speed. A phase below the balance point is *memory-bound*: it waits for memory, so more arithmetic speed does not help. A phase above it is *compute-bound*: it waits for arithmetic. A worked example is in [glossary: hardware and performance](../glossary/hardware-and-performance.md).

```text
Which limit applies: operator intensity (FLOP/byte) vs a device's balance point
(spacing not to scale)

  54            164           321           543           1481
  |             |             |             |             |
  expert        RTX 4090      vision        VLM           Jetson Thor
                balance                                   balance

  Left of a balance point = memory-bound, right = compute-bound.
  RTX 4090: expert is memory-bound; vision and VLM are compute-bound.
  Thor:     all three phases are left of 1481, so all three are memory-bound.
```

```text
RTX 4090, pi0, 3 cameras: measured latency vs roofline  (1 # = 3 ms)

  naive PyTorch 113.9 |######################################
  openpi JAX     67.6 |#######################
  tuned Triton   36.8 |############
  roofline       30.4 |##########    VLA-Perf bound
  roofline       26.7 |#########    Realtime-VLA bound
```
The first drawing is the phase structure of the Summary, the second is the first two bullets of Details, and the third is the 4090 row of the table below.

## Details
**Phase structure (π0-class, 3 cameras, 800 tokens; [VLA-Perf](../resources/serving/vla-perf.md))**
- Roofline latency (Table 3: 800 tokens, chunk 50, 10 steps): Jetson Thor vision 6.1 ms + VLM 20.3 ms + action expert 26.2 ms = 52.6 ms (19.0 Hz); RTX 4090 4.0 + 19.8 + 7.3 = 31.1 ms; A100 16.2 ms; H100 6.2 ms. The 30.4 ms in the table below is the same paper's Table 1 (empty prompt, chunk 63), a different configuration.
- Operator intensity (FLOPs/byte): vision 321, VLM 543, action expert 54. Balance points: 164 (RTX 4090), 1481 (Thor, with 273 GB/s LPDDR5X), so on Thor even the VLM is memory-bound.
- Other sources report the same shape: VLM decoder layer about 840 FLOPs/byte vs expert 64.5 (ridge points 330 RTX 4090, 208 AGX Orin, 945 Thor in [XPU characterization](../resources/serving/vla-xpu-characterization.md)); prefix 256–530 vs expert about 50 FLOPs/byte in [vla.cpp](../resources/serving/vla-cpp.md). Ridge points differ between papers because each assumes different peak throughput; the ordering is consistent.
- SM utilization (a measured profile in [XPU characterization](../resources/serving/vla-xpu-characterization.md)): VLM over 90%, action expert 20–40%, and the expert takes about 2× the VLM's latency. This differs from the roofline above, where the expert is shorter than the VLM on the RTX 4090 (7.3 vs 19.8 ms) and 1.3× longer on Thor (26.2 vs 20.3 ms); the profile's device and configuration are not matched to those rows.

**Scaling and knobs ([VLA-Perf](../resources/serving/vla-perf.md))**
- The step count T of the expert loop ranges from 4 (GR00T N1) to 10 (π0, SmolVLA) ([flow-step reduction](flow-step-reduction.md)). In π0 the prefix keys and values are computed once and reused by every step ([architecture overview](vla-architecture-overview.md)).
- Latency scales about linearly with parameters per component (π0-L 9.1B: 3.9 Hz on Thor); flow steps scale the expert linearly (10 → 50 steps: 5× expert, 2.15× total); chunk size barely matters; long KV context limits Thor/4090 to about 100 past timesteps.
- Split of time varies by model: on an RTX 5070, SmolVLA vision 38% + backbone 14%; π0 vision 21% + backbone 54%; expert nearly half of SmolVLA and GR00T-N1.6 time even with cached features ([vla.cpp](../resources/serving/vla-cpp.md)). For a 7B CogACT profile on an A40: LLM 134.5 ms, DiT 51.5 ms, vision 24.9 ms ([EfficientVLA](../resources/compression/efficientvla.md)).

**Roofline vs measured (π0, about three cameras)**

| Device      | Roofline                                                   | Measured                                                                                                                                                                                                                        | Source                                                                                                  |
| ----------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| RTX 4090    | 30.4 ms (VLA-Perf); 26.7 ms (Realtime-VLA, 27.6 with sync) | 36.8 ms tuned Triton; 67.6 ms openpi JAX; 113.9 ms naive PyTorch                                                                                                                                                                | [Realtime-VLA](../resources/serving/realtime-vla.md), [VLA-Perf](../resources/serving/vla-perf.md)      |
| Jetson Thor | 52.6 ms                                                    | π0: 246 ms baseline, 163 ms compiled ([XPU](../resources/serving/vla-xpu-characterization.md)); 448 ms naive PyTorch ([Jetson-PI](../resources/serving/jetson-pi.md)). π0.5: 458 ms naive, 310 ms after system work (Jetson-PI) | [XPU](../resources/serving/vla-xpu-characterization.md), [Jetson-PI](../resources/serving/jetson-pi.md) |
| AGX Orin    | not modeled                                                | 921 ms (π0 baseline); 1403 ms at 50 W, 2269 ms at 30 W (π0 naive)                                                                                                                                                               | XPU, Jetson-PI                                                                                          |

Measured runs use different chunk sizes, camera counts and frameworks; treat the table as an order-of-magnitude picture (naive software 4–9× above roofline: 113.9 vs 26.7 ms is 4.3× on the 4090 and 448 vs 52.6 ms is 8.5× on Thor; tuned software 36.8 vs 26.7 ms is 1.4× on a 4090). VLA-Perf itself reports real Triton at 73–83% of its roofline.

**Where the software gap comes from (4090, [Realtime-VLA](../resources/serving/realtime-vla.md))**
- π0 launches over a thousand kernels per call (1378 matmuls). Inter-kernel overhead: 12.9 ms in PyTorch, 1.7 ms with a CUDA graph, 0.9 ms with a software grid barrier. Graph capture alone roughly halved latency (106.5 → 43.5 ms for two views); simplifying the graph, tuned GEMM tiles and fused epilogues took it to 27.3 ms.
- Tile quantization also matters: a 512×1152×1152 GEMM split into 144 blocks did not divide across 128 SMs.
- torch.compile gains vary by device (2.9× on RTX 4090 but 1.5× on Thor and 2.3× on Ascend 310P in [XPU](../resources/serving/vla-xpu-characterization.md)).

**Related:** how precision changes these phases is in [quantization](quantization.md) (which is about numeric formats and kernels, not phase structure), and per-technique speedups measured against these baselines are collected in [technique comparison](technique-comparison.md).

**Autoregressive and reasoning VLAs**
- OpenVLA generates 7 tokens sequentially; parallel decoding cut latency 4× and chunking gave 26× throughput ([OpenVLA-OFT](../resources/models/openvla-oft.md)). π0-FAST decodes 30–60 tokens through the full LLM, about 750 ms per chunk vs about 100 ms for diffusion π0 on the same GPU ([FAST](../resources/models/fast-tokenizer.md)).
- For a reasoning VLA (MolmoAct-7B) generation was about 75% of latency, and Thor's 5× compute over Orin gave only 1.4× speedup ([edge bottleneck characterization](../resources/serving/vla-edge-bottleneck-characterization.md)).

**Memory footprints:** OpenVLA 15 GB in bf16; π0 about 14 GB; SmolVLA about 2 GB ([LeRobot docs](../resources/serving/lerobot-async-inference-docs.md)); KV cache for one frame set is small (0.01 GB in VLA-Perf's π0 model) but grows linearly with history.

**Implications for accelerator design (inferences from the data above)**
- The prefill phase needs high dense-MAC throughput and benefits from token-count reductions only while compute-bound ([token pruning and caching](token-pruning-and-caching.md)).
- The expert loop is limited by re-reading its weights each step; keeping expert weights resident in fast on-chip memory across steps addresses this directly ([edge budget estimate](edge-budget-estimate.md)).
- Shapes are static (fixed tokens, steps and chunk), so whole-graph static scheduling is possible; dynamic schemes need care ([layer skipping and pruning](layer-skipping-and-pruning.md)).

## Open questions
- No source gives a per-operator profile for SmolVLA on an accelerator; the vision-encoder share for 512×512 inputs is not reported in the papers read.
