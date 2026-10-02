---
type: paper
tags: [token-pruning, differentiable, gumbel-softmax, openvla-oft, training-aware]
sources: [arxiv:2509.12594, https://arxiv.org/abs/2509.12594, https://liauto-research.github.io/LightVLA]
---
# The Better You Learn, The Smarter You Prune: Differentiable Token Pruning for VLAs (LightVLA)

Jiang, Jiang, Ma, et al. (Li Auto, Tsinghua, ICT-CAS), arXiv 2509.12594 (v2, Sept 2025).

## Summary
LightVLA prunes visual tokens inside a fine-tuned OpenVLA-OFT using parameter-free, instruction-conditioned queries and Gumbel-softmax selection, so the number of kept tokens is learned rather than fixed. It keeps about 78 of 512 visual tokens on average on LIBERO and reports lower FLOPs and latency with higher success. It needs a fine-tuning run but no attention scores, so it works with inference frameworks (vLLM, SGLang) that do not expose them.

## Key claims
- **Method (§III):** queries come from cross-attention between visual tokens and language tokens (no weights); each query picks its highest-scoring visual token; unique selections form the pruned set. Training uses Gumbel-softmax with a straight-through estimator and a decaying noise bound; inference uses plain argmax. Position IDs and the [CLS] token are preserved.
- **Training (§IV-A):** LoRA rank 32 on OpenVLA-OFT for 40,000 steps, batch 64, 8 H20 GPUs.
- **Results (Table I–II, LIBERO):** avg 97.4% with 78 tokens on average (per suite 90 ± 15, 78 ± 11, 64 ± 10, 79 ± 11). FLOPs 8.8 → 3.6 T (−59.1%), latency 34 → 21 ms (−38.2%) on H20.
- **Baseline caveat:** the "+2.6%" gain is against the authors' reproduced OpenVLA-OFT (94.8%); the published OpenVLA-OFT figure is 97.1% ([OpenVLA-OFT](../models/openvla-oft.md)), so against the published number the accuracy gain is small. Table II also mixes GPUs across rows (RTX 4090, H100, A100, H20), so its latency column is not a controlled comparison.
- **Sparsity analysis (Table IV):** adding k random tokens or removing 10% of selected ones both reduce success (97.4 → 96.8 / 96.6).
- **Variants (§V):** learnable-query LightVLA* pruning at the vision encoder or LLM layer 1–3 also improves on the baseline (96.2–97.0).
- **Limitations:** LIBERO only, no real-robot evaluation, requires fine-tuning.

## Related
See also: [VLA-Cache](vla-cache.md), [EfficientVLA](efficientvla.md), [pruned-VLA recovery](pruned-vla-recovery.md).
