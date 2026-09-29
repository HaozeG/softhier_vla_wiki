---
type: concept
tags: [workload, roofline, memory-bound, prefill, action-expert, latency-breakdown]
sources: [resources/vla-perf.md, resources/realtime-vla.md, resources/vla-xpu-characterization.md, resources/vla-edge-bottleneck-characterization.md, resources/vla-cpp.md, resources/jetson-pi.md, resources/pi0.md, resources/openvla-oft.md, resources/fast-tokenizer.md, resources/efficientvla.md]
---
# Inference workload characterization

## Summary
A flow-matching VLA call has three phases: vision encoding and VLM prefill (large matrix multiplies over hundreds of tokens, compute-bound on GPUs) and an iterative action-expert loop (few tokens, weights re-read every step, memory-bound). On bandwidth-poor edge devices all three can become memory-bound. Measured latencies sit several times above the roofline unless launch and synchronization overheads are engineered away; autoregressive-action VLAs add a fourth, decode-dominated phase.

## Details
**Phase structure (π0-class, 3 cameras, 800 tokens; [VLA-Perf](../resources/vla-perf.md))**
- Roofline latency: Jetson Thor vision 6.1 ms + VLM 20.3 ms + action expert 26.2 ms = 52.6 ms (19.0 Hz); RTX 4090 4.0 + 19.8 + 7.3 = 31.1 ms; A100 16.2 ms; H100 6.2 ms.
- Operator intensity (FLOPs/byte): vision 321, VLM 543, action expert 54. Balance points: 164 (RTX 4090), 1481 (Thor, with 273 GB/s LPDDR5X), so on Thor even the VLM is memory-bound.
- Other sources report the same shape: VLM decoder layer about 840 FLOPs/byte vs expert 64.5 (ridge points 330 RTX 4090, 208 AGX Orin, 945 Thor in [XPU characterization](../resources/vla-xpu-characterization.md)); prefix 256–530 vs expert about 50 FLOPs/byte in [vla.cpp](../resources/vla-cpp.md). Ridge points differ between papers because each assumes different peak throughput; the ordering is consistent.
- SM utilization: VLM over 90%, action expert 20–40%, while the expert takes about 2× the VLM's time on the devices they profiled.

**Scaling and knobs ([VLA-Perf](../resources/vla-perf.md))**
- Latency scales about linearly with parameters per component (π0-L 9.1B: 3.9 Hz on Thor); flow steps scale the expert linearly (10 → 50 steps: 5× expert, 2.15× total); chunk size barely matters; long KV context limits Thor/4090 to about 100 past timesteps.
- Split of time varies by model: on an RTX 5070, SmolVLA vision 38% + backbone 14%; π0 vision 21% + backbone 54%; expert nearly half of SmolVLA and GR00T-N1.6 time even with cached features ([vla.cpp](../resources/vla-cpp.md)). For a 7B CogACT profile on an A40: LLM 134.5 ms, DiT 51.5 ms, vision 24.9 ms ([EfficientVLA](../resources/efficientvla.md)).

**Roofline vs measured (π0, about three cameras)**

| Device | Roofline | Measured | Source |
|---|---|---|---|
| RTX 4090 | 30.4 ms (VLA-Perf); 26.7 ms (Realtime-VLA, 27.6 with sync) | 36.8 ms tuned Triton; 67.6 ms openpi JAX; 113.9 ms naive PyTorch | [Realtime-VLA](../resources/realtime-vla.md), [VLA-Perf](../resources/vla-perf.md) |
| Jetson Thor | 52.6 ms | π0: 246 ms baseline, 163 ms compiled ([XPU](../resources/vla-xpu-characterization.md)); 448 ms naive PyTorch ([Jetson-PI](../resources/jetson-pi.md)). π0.5: 458 ms naive, 310 ms after system work (Jetson-PI) | [XPU](../resources/vla-xpu-characterization.md), [Jetson-PI](../resources/jetson-pi.md) |
| AGX Orin | not modeled | 921 ms (π0 baseline); 1403 ms at 50 W, 2269 ms at 30 W (π0 naive) | XPU, Jetson-PI |

Measured runs use different chunk sizes, camera counts and frameworks; treat the table as an order-of-magnitude picture (naive software 4–9× above roofline; tuned software within 1.3–1.4× on a 4090). VLA-Perf itself reports real Triton at 73–83% of its roofline.

**Where the software gap comes from (4090, [Realtime-VLA](../resources/realtime-vla.md))**
- π0 launches over a thousand kernels per call (1378 matmuls). Inter-kernel overhead: 12.9 ms in PyTorch, 1.7 ms with a CUDA graph, 0.9 ms with a software grid barrier. Graph capture alone roughly halved latency (106.5 → 43.5 ms for two views); simplifying the graph, tuned GEMM tiles and fused epilogues took it to 27.3 ms.
- Tile quantization also matters: a 512×1152×1152 GEMM split into 144 blocks did not divide across 128 SMs.
- torch.compile gains vary by device (2.9× on RTX 4090 but 1.5× on Thor and 2.3× on Ascend 310P in [XPU](../resources/vla-xpu-characterization.md)).

**Related:** how precision changes these phases is in [quantization](quantization.md) (which is about numeric formats and kernels, not phase structure), and per-technique speedups measured against these baselines are collected in [technique comparison](technique-comparison.md).

**Autoregressive and reasoning VLAs**
- OpenVLA generates 7 tokens sequentially; parallel decoding cut latency 4× and chunking gave 26× throughput ([OpenVLA-OFT](../resources/openvla-oft.md)). π0-FAST decodes 30–60 tokens through the full LLM, about 750 ms per chunk vs about 100 ms for diffusion π0 on the same GPU ([FAST](../resources/fast-tokenizer.md)).
- For a reasoning VLA (MolmoAct-7B) generation was about 75% of latency, and Thor's 5× compute over Orin gave only 1.4× speedup ([edge bottleneck characterization](../resources/vla-edge-bottleneck-characterization.md)).

**Memory footprints:** OpenVLA 15 GB in bf16; π0 about 14 GB; SmolVLA about 2 GB ([LeRobot docs](../resources/lerobot-async-inference-docs.md)); KV cache for one frame set is small (0.01 GB in VLA-Perf's π0 model) but grows linearly with history.

**Implications for accelerator design (inferences from the data above)**
- The prefill phase needs high dense-MAC throughput and benefits from token-count reductions only while compute-bound ([token pruning and caching](token-pruning-and-caching.md)).
- The expert loop is limited by re-reading its weights each step; keeping expert weights resident in fast on-chip memory across steps addresses this directly ([edge budget estimate](edge-budget-estimate.md)).
- Shapes are static (fixed tokens, steps and chunk), so whole-graph static scheduling is possible; dynamic schemes need care ([layer skipping and pruning](layer-skipping-and-pruning.md)).

## Open questions
- No source gives a per-operator profile for SmolVLA on an accelerator; the vision-encoder share for 512×512 inputs is not reported in the papers read.
