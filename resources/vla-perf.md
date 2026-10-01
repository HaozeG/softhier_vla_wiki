---
type: paper
tags: [vla, performance-model, roofline, jetson-thor, serving, latency]
sources: [arxiv:2602.18397, https://arxiv.org/abs/2602.18397, https://github.com/NVlabs/vla-perf]
---
# How Fast Can I Run My VLA? Demystifying VLA Inference Performance with VLA-Perf

Jiang, Clemons, Sankaralingam, Kozyrakis (NVIDIA Research), arXiv 2602.18397 (Feb 2026). Code: NVlabs/vla-perf.

## Summary
VLA-Perf is an analytical, roofline-based latency model for arbitrary VLA architectures and inference systems (on-device, edge server, cloud, with a network model). Using π0-derived model variants, the paper distils 15 takeaways about model scaling, denoising steps, long context, asynchrony, dual-system pipelines and device/edge/cloud placement. It is an upper-bound (optimistic) model, validated against an optimized Triton π0 implementation on an RTX 4090.

## Key claims
- **Method (§3):** per-operator latency T_o = max(FLOPs/peak, Bytes/bandwidth); component latency is the sum over operators; total latency adds network transfer T = NetLat + Bytes/NetBW. BF16 (or FP16) assumed. Real 10 Hz is called "acceptable" and 100 Hz "high-performance", relative to 24–60 Hz cameras.
- **Fidelity (Table 1):** on RTX 4090, π0 with 10 flow steps and chunk 63: roofline 14.7 / 22.5 / 30.4 ms vs real Triton 20.0 / 27.3 / 36.8 ms for 1 / 2 / 3 cameras, i.e. 73–83% of roofline.
- **Baseline π0 (Table 3, 3 cameras of 224×224 at 256 tokens each, 800 total tokens):**
  - Jetson Thor: vision 6.06 ms, VLM 20.30 ms, action 26.20 ms, total 52.57 ms (19.0 Hz).
  - RTX 4090: vision 4.02 ms, VLM 19.79 ms, action 7.25 ms, total 31.06 ms (32.2 Hz). A100: 16.20 ms. H100: 6.15 ms. B100: 3.18 ms.
- **Compute vs memory bound (Table 4):** the action expert (operator intensity 54 FLOPs/byte) is memory-bound everywhere; vision (321) and VLM (543) are compute-bound on GPUs, but on Jetson Thor (balance point 1481 FLOPs/byte; LPDDR at 270 GB/s vs 1 TB/s on 4090 and 8 TB/s on B100) all three components are memory-bound. The paper compares this to LLM prefill (compute-bound) vs decode (memory-bound).
- **Scaling (Table 5):** latency scales about linearly with parameters. π0 (2.7B): 19.0 Hz on Thor. π0-L (9.1B): 3.9 Hz on Thor. π0-XL (16.7B): 2.1 Hz on Thor; out of memory on the 4090. B100 still reaches 9.6 Hz at 81B.
- **Long context (Table 6):** with a growing VLM KV cache, Thor and 4090 are limited to about 100 past timesteps (about 8 Hz); 1000 steps give 1.3 Hz on Thor.
- **Denoising steps vs chunk size (Fig. 6, takeaway 6):** flow steps scale action-expert latency linearly (10 → 50 steps: 5× expert, 2.15× end-to-end). Chunk size has a negligible effect (50 → 250: +40% expert, +11% end-to-end) because the expert is memory-bound.
- **Dual system (Table 9):** async System 1 / System 2 gives 1.46× (5 Hz S2 cap) or 1.30× (10 Hz cap) on Thor; up to 2.24× on B100 with 10G Ethernet; only 1.05× over 5G.
- **Placement (takeaways 13–15):** Thor reaches 10 Hz for π0 but 100 Hz needs about 5× more (smaller model, fewer flow steps, lower precision). Edge-server 4090 achieves 10 Hz even over 4G; 100 Hz needs datacenter GPUs and fast networks. Cloud reaches 100 Hz only with async inference.

## Relevance to SoftHier-VLA
This is the best available public model for reasoning about where a VLA is bound. Its memory-bound action expert and bandwidth-limited edge GPU are the central inputs to [inference workload characterization](../knowledge/inference-workload-characterization.md) and [edge hardware and the 10 TOPS gap](../knowledge/edge-hardware-and-the-10-tops-gap.md). Note it models only Thor-class edge devices and assumes BF16; nothing near 10 TOPS is evaluated.

See also: corroborating measurements in [vla.cpp](vla-cpp.md), [XPU study](vla-xpu-characterization.md) and [Jetson-PI](jetson-pi.md); validation source [Realtime-VLA](realtime-vla.md); device specs in [Jetson specs](nvidia-jetson-platform-specs.md).
