---
type: paper
tags: [runtime, quantization, vla, wam, heterogeneous, recent]
sources: [arxiv:2607.02501, https://arxiv.org/abs/2607.02501, https://github.com/SEU-PAISys/Embodied.cpp]
---
# Embodied.cpp: A Portable Inference Runtime of Embodied AI Models on Heterogeneous Robots

Xu, Li, Wu, Han, Li, Hua, Jiang, Cao, Li, Zhong, Wang (Southeast University, Nanjing University, Microsoft Research, Tsinghua AIR), arXiv 2607.02501 (v3, Aug 2026). Recent paper, not yet independently reproduced.

## Summary
A C++ runtime for VLA models and world-action models built around a five-layer structure (input adapters, sequence builders, backbone execution, head plugins, deployment adapters) with multi-rate execution and latency-first batch-1 inference. It names Jetson, "RK-based boards" and x86 edge boxes as target device classes, but its evaluation reports normalized latency, success rate and VRAM for π0.5, GR00T N1.7 and HY-VLA and does not report any Rockchip measurement.

## Key claims
- **Runtime contract (§3):** multi-rate execution (encoders, backbone and action heads at different rates), latency-first small-batch inference (graph replay, buffer reuse, fusion) and extensible operator and I/O support. It positions itself against llama.cpp, ONNX Runtime and [vla.cpp](vla-cpp.md) as VLA-centric.
- **Normalized results (Table 3; Python baseline = 1.00):**
  - π0.5: latency 0.90 (C++), 0.88 (8-bit), 0.95 (6-bit), 0.88 (4-bit); success 0.92 / 0.90 / 0.93 / **0.70**; VRAM 0.60 / 0.41 / 0.35 / 0.30.
  - GR00T N1.7: latency 0.72 / 0.70 / 0.70 / 0.65; success 0.96 / 0.97 / 0.97 / 0.96; VRAM 0.93 / 0.57 / 0.48 / 0.38.
  - HY-VLA: latency 0.48 / 0.38 / 0.39 / 0.37; success about 1.0 throughout; VRAM 0.68 / 0.27 / 0.25 / 0.23.
  - Overall claim: 1.05–2.70× speedups and 7–77% lower VRAM at near-baseline success for most configurations.
- **World-action models (Table 4):** Cosmos3 49% → 48% success, VRAM 21.8 → 19.5 GB; LingBot-VA 100% → 98%, 24.75 → 16.4 GB.
- **What it does not give:** absolute latencies, hardware named per row, or any NPU result; the RK-board mention is motivation only.

## Related
See also: [vla.cpp](vla-cpp.md).
