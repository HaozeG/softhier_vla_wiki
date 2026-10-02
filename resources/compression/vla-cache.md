---
type: paper
tags: [token-caching, training-free, kv-cache, openvla, openvla-oft]
sources: [arxiv:2502.02175, https://arxiv.org/abs/2502.02175, https://vla-cache.github.io]
---
# VLA-Cache: Efficient Vision-Language-Action Manipulation via Adaptive Token Caching

Xu, Wang, Xia, Zhu, Huang, Xu (University of Sydney, SJTU), arXiv 2502.02175 (v2, Oct 2025; NeurIPS 2025).

## Summary
A training-free, plug-and-play method that reuses cached key/value entries of visual tokens that barely change between consecutive frames, while always recomputing tokens that the decoder attends to as task-relevant. A layer-adaptive rule sets the reuse ratio per decoder layer from attention entropy. It is evaluated on Llama-2-based VLAs (OpenVLA, OpenVLA-OFT, CogACT) on an RTX 4090.

## Key claims
- **Static-token test (§3.2, App. D):** per-patch cosine similarity between frame t and t−1 above τ = 0.996 (0.85 on the real robot), keep top-k = 100; exclude task-relevant tokens using decoder attention (τ_task = 0.5); per-layer reuse fraction α_l = min(k·Σ R_j, 1) from the layer-to-layer entropy reduction.
- **Why filtering matters (Table 1, OpenVLA on LIBERO-Spatial):** naive static reuse drops success from 84.4% to 74.2%; excluding task-relevant tokens recovers 82.6%; layer-adaptive reuse gives 83.8% at 32.2 ms vs 51.6 ms baseline.
- **LIBERO (Table 2, RTX 4090):** OpenVLA avg success 75.0 → 74.7, FLOPs 1.864 → 1.355 T, latency 51.91 → 31.83 ms (4.23 → 4.59 Hz). OpenVLA-OFT 96.8 → 97.4, FLOPs 4.013 → 3.097 T, latency 79.05 → 62.59 ms (65.1 → 79.0 Hz).
- **CogACT / SIMPLER (Table 3):** avg 74.8 → 74.4 (visual matching), FLOPs 1.847 → 1.496 T, latency 54.29 → 39.63 ms.
- **Real robot (Table 5, Kinova Jaco2):** OpenVLA 82.1% → 84.6%; latency 64.16 → 51.85 ms.
- **Versus VLM token pruning:** FastV did not speed up OpenVLA (53.28 vs 51.91 ms) and SparseVLM slowed it (83.39 ms), with success dropping to 64.7. The authors attribute this to VLAs emitting very short outputs (about 7 tokens) and to intra-frame pruning disturbing spatial detail.
- **Limitations (App. A):** gains shrink in dynamic scenes; only Llama-2-decoder VLAs tested; π0's Gemma backbone untried.
- **Caveat from a later paper:** [EfficientVLA](efficientvla.md) reports that on CogACT VLA-Cache yields only 1.38× because it does not touch the LLM's memory-bound cost or the action head.

## Related
See also: [LightVLA](lightvla.md), [EfficientVLA](efficientvla.md), [OpenVLA-OFT](../models/openvla-oft.md).
