---
type: concept
tags: [token-pruning, token-caching, visual-tokens, kv-cache, training-free]
sources: [resources/vla-cache.md, resources/lightvla.md, resources/efficientvla.md, resources/survey-efficient-vla-guan.md, resources/survey-efficient-vla-yu.md, resources/smolvla.md, resources/gr00t-n1.md, resources/clp-layer-pruning.md]
---
# Token pruning and caching

## Summary
Visual tokens dominate a VLA's prefix sequence, so pruning or reusing them is a natural target, but the gains are smaller and more conditional than in VLMs. Methods borrowed from VLMs (FastV, SparseVLM) gave no speedup on OpenVLA and hurt accuracy; VLA-specific methods exploit temporal redundancy (cache static tokens across frames) or learn which tokens matter (LightVLA). Speedup saturates once the LLM becomes memory-bound, and modern small VLAs already use only 64 tokens per frame.

```text
visual tokens per frame?
|
+-- 64 (SmolVLA, GR00T N1: pixel shuffle, no tiling)
|     little left to prune
|
+-- 256-512 (7B OpenVLA family)
      +-- attention pruning inside one frame (FastV, SparseVLM)
      |     about 1.0x or slower; disturbs spatial detail
      +-- reuse static tokens across frames (VLA-Cache)
      |     no training; needs a relevance filter
      +-- learned selection (LightVLA)
      |     fine-tune; variable length conflicts with static shapes
      +-- any of them: speedup saturates (tokens alone about 1.23x)
            once LLM weight reads and the action head set the floor
```

## Details
**Methods and measured results**

| Method                       | Idea                                                                                                | Training  | Result                                                                                                                    | Source                                       |
| ---------------------------- | --------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| VLA-Cache                    | reuse KV of tokens whose patches barely changed; recompute task-relevant ones; layer-adaptive reuse | none      | OpenVLA LIBERO 75.0 → 74.7 avg, latency 51.9 → 31.8 ms, FLOPs −27%; OpenVLA-OFT 96.8 → 97.4, 65 → 79 Hz (RTX 4090)        | [VLA-Cache](../resources/vla-cache.md)       |
| LightVLA                     | parameter-free instruction-driven queries pick tokens with Gumbel-softmax                           | fine-tune | 512 → about 78 tokens on OFT; FLOPs −59%, 34 → 21 ms (H20), 94.8 → 97.4% vs its reproduced baseline (published OFT 97.1%) | [LightVLA](../resources/lightvla.md)         |
| EfficientVLA token step      | top-K task-relevant plus diverse tokens                                                             | none      | 56 of 256 tokens alone: 1.23× (saturates)                                                                                 | [EfficientVLA](../resources/efficientvla.md) |
| FastV / SparseVLM on OpenVLA | attention-based pruning inside one frame                                                            | none      | FastV about 1.0× (53.3 vs 51.9 ms), SparseVLM slower (83.4 ms) and 64.7% success                                          | [VLA-Cache](../resources/vla-cache.md)       |

**What is established**
- **Why VLM pruning fails in VLAs:** the output is a short action sequence (about 7 tokens for OpenVLA), so prefill dominates but intra-frame pruning disturbs spatial detail that manipulation needs ([VLA-Cache](../resources/vla-cache.md), [LightVLA](../resources/lightvla.md)).
- **Reuse needs a relevance filter:** naively reusing every static token dropped OpenVLA from 84.4% to 74.2% on LIBERO-Spatial; excluding attention-relevant tokens recovered 82.6% ([VLA-Cache](../resources/vla-cache.md)).
- **Saturation:** once tokens are pruned enough, latency is set by the LLM's weight reads and the action head, not token count; EfficientVLA found token pruning alone limited to 1.23× while combining it with layer pruning and action-head caching gave 1.93× ([EfficientVLA](../resources/efficientvla.md)).
- **Small VLAs start low:** SmolVLA and GR00T N1 use 64 tokens per frame by design (pixel shuffle, no tiling), which leaves little to prune ([SmolVLA](../resources/smolvla.md), [GR00T N1](../resources/gr00t-n1.md)); pruning helped most on 7B models with 256–512 tokens.
- **Benchmarks:** most results are LIBERO/SIMPLER with a 7B Llama-2 backbone; π0's Gemma backbone was untested by VLA-Cache, and in [CLP](../resources/clp-layer-pruning.md)'s comparison table the token methods scored 88.9–94.4% vs 96.6% for OpenVLA-OFT (FastV 93.3%, EfficientVLA 88.9%, ADP 94.4%).

**Implementation considerations (inferences)**
- Attention-score-based pruning is incompatible with fused attention kernels that do not expose scores; LightVLA and the SVD-based FlashVLA variant avoid them ([Guan et al.](../resources/survey-efficient-vla-guan.md)).
- Caching needs per-layer KV for the previous frame (storage) and variable-length gathers; learned pruning yields variable sequence lengths (90 ± 15 tokens on LIBERO-Spatial), which conflicts with static shapes and CUDA-graph or static tile schedules unless padded to a maximum.
- The [surveys](../resources/survey-efficient-vla-yu.md) list further caching schemes (HybridVLA, CronusVLA, FlashVLA action reuse, EfficientVLA feature caching) that were not read here.

## Open questions
- Effect on π0/SmolVLA-class models with fewer tokens and a separate expert; reported evidence is thin and mostly on OpenVLA-family models.
- Robustness in dynamic scenes: VLA-Cache's gains shrink as more tokens change.
