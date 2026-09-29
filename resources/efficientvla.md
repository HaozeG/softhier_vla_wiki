---
type: paper
tags: [layer-pruning, token-pruning, feature-caching, training-free, diffusion-vla, cogact]
sources: [arxiv:2506.10100, https://arxiv.org/abs/2506.10100]
---
# EfficientVLA: Training-Free Acceleration and Compression for Vision-Language-Action Models

Yang, Wang, Wen, Luo, Zou, Zhang, Wen, Zhang (SJTU and others), arXiv 2506.10100 (June 2025, under review at posting).

## Summary
A training-free framework for diffusion-head VLAs that combines three steps: prune redundant LLM layers (by input/output cosine similarity), prune visual tokens by task relevance plus diversity, and cache attention/MLP features across denoising steps in the action head. On CogACT in SIMPLER it reports 1.93× speedup and 28.9% of FLOPs for a 0.6-point success drop. It also gives a module-level profile showing why token pruning alone saturates.

## Key claims
- **Profile of CogACT (Table 1, A40):** vision 802.3M params, 24.9 ms, 405.5 GFLOPs; language (Llama-2 7B) 6738.9M, 134.5 ms, 3726.6 GFLOPs; action DiT 89M, 51.5 ms, 58.0 GFLOPs (10 denoising steps). The language module and the iterative action head dominate latency.
- **Memory-bound saturation (Fig. 1a, Table 4):** visual token pruning helps only while the model is compute-bound; below about 22% of tokens (56 of 256) further pruning barely improves latency because the LLM becomes memory-bound. Token pruning alone with 56 tokens: 1.23× (Table 5).
- **Layer pruning (§3.2):** importance I(ℓ) = 1 − mean cosine(input, output hidden state) over a calibration set; remove the n lowest-scoring layers, non-contiguously. A further 25% MLP sparsity uses a PruneNet configuration.
- **Token pruning (§3.3):** keep K_key = 4–8 top task-relevant tokens, then add task-relevant and diverse tokens (diversity by cosine dissimilarity) up to K_final.
- **Action-head cache (§3.4):** recompute attention and MLP features only every N = 5 steps and reuse otherwise.
- **Main results (Table 2, SIMPLER visual matching):** CogACT 74.8% avg. EfficientVLA with L = 22 of 32 layers, T = 56 tokens: 74.2% avg, 28.9% FLOPs, 1.93× speedup, 4.86B params. L = 28, T = 112: 76.4%, 45.1% FLOPs, 1.59×. VLA-Cache 74.4% / 1.38×; FastV 74.1% / 1.21×; random dropping to 112 tokens collapses to 20.9%.
- **Scaling (Table 3):** speedup grows with a larger action head (CogACT-Large 308M: 2.0×, 76.7 → 76.1).
- **Limitations (App. C):** only CogACT tested (few open diffusion VLAs at the time); fixed cache interval; training-free methods reach less compression than training-aware ones.

## Relevance to SoftHier-VLA
Its per-module time/FLOP split is a template for workload analysis, and the memory-bound saturation result is the central caution for token-pruning claims. See [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md), [token pruning and caching](../knowledge/token-pruning-and-caching.md), and [flow-step reduction](../knowledge/flow-step-reduction.md). Measured on an A40 GPU, not an edge device.

See also: [VLA-Cache](vla-cache.md), [CLP](clp-layer-pruning.md), [pruned-VLA recovery](pruned-vla-recovery.md), [OpenVLA-OFT](openvla-oft.md), and the surveys [Yu et al.](survey-efficient-vla-yu.md) and [Guan et al.](survey-efficient-vla-guan.md).
