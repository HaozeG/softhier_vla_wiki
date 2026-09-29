---
type: concept
tags: [taxonomy, survey, efficiency, map, naming]
sources: [resources/survey-efficient-vla-yu.md, resources/survey-efficient-vla-guan.md, resources/survey-vla-embodied-ai-ma.md, resources/survey-vla-action-tokenization.md, resources/vla-perf.md]
---
# VLA efficiency taxonomy

## Summary
See the [edge serving overview](vla-edge-serving-overview.md) for the reading path.

Two dedicated surveys organize VLA efficiency differently: [Yu et al.](../resources/survey-efficient-vla-yu.md) by lifecycle (model design, training, data) and [Guan et al.](../resources/survey-efficient-vla-guan.md) by pipeline stage (architecture, perception features, action generation, training and inference). For serving on edge hardware, this wiki uses a third cut by *what is executed per control step*, mapping each technique to a note. The surveys agree on the main gap: efficiency methods are mostly borrowed from VLM/LLM work and rarely address robot-specific issues (temporal consistency, execution latency), and neither contains hardware-level latency analysis.

## Details
**Map from survey categories to wiki notes**

| What is executed per control step | Technique family | Note |
|---|---|---|
| Vision encoder and projector | fewer/smaller images, pixel shuffle, no tiling, encoder quantization | [token pruning and caching](token-pruning-and-caching.md), [quantization](quantization.md) |
| VLM prefill | layer skipping/pruning, width pruning, token pruning/caching, quantization | [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [quantization](quantization.md) |
| Action decoding | discrete vs parallel vs flow head; step reduction; feature caching; streaming | [action representation and chunking](action-representation-and-chunking.md), [flow-step reduction](flow-step-reduction.md) |
| Whole call | kernels, graphs, runtimes | [serving methods](serving-methods.md) |
| Across calls | chunking, async, chunk stitching, dual-system, placement | [serving methods](serving-methods.md) |
| Training-time | LoRA, distillation, pretraining recipes, data efficiency | [VLA architecture overview](vla-architecture-overview.md); surveys only |

Surveys' training-only and data-collection pillars (efficient pretraining, RL, simulation data) are outside this wiki's serving scope; consult [Yu et al.](../resources/survey-efficient-vla-yu.md) for them.

**Method families the surveys name (mostly not read here)**
- Efficient attention and linear-time/state-space backbones (SARA-RT, RoboMamba, FlowRAM), parallel decoding and speculative decoding for VLAs (PD-VLA, CEED-VLA, Spec-VLA), mixture-of-experts and hierarchical designs, KV-cache and token caching (HybridVLA, CronusVLA, FlashVLA variants), distillation and pruning recovery (GLUESTICK, RLRC), quantization-aware training (SQIL).
- Treat their inclusion as a pointer, not evidence; only methods with their own note under `resources/` were read from the primary paper.

**Naming collisions to watch**
- "FlashVLA" names three unrelated works: an SVD-based token-pruning method and a token-aware action-reuse method (both described by the surveys) and the UCSD/MIT streaming action decoder ([FlashVLA](../resources/flashvla-streaming.md)). Cite by arXiv ID.
- "SmolVLA" appears with 0.24B, 0.45B and 2.25B backbones; check the size ([SmolVLA](smolvla.md)).
- "Edge" in papers ranges from Jetson Thor (128 GB, 40–130 W) to a Raspberry Pi CPU ([edge hardware](edge-hardware-and-the-10-tops-gap.md)).
- VLA-Perf's "latency" is a roofline lower bound, not a measurement ([VLA-Perf](../resources/vla-perf.md)).

**Source tiers used in this wiki**
- Primary papers with numbers and first-party documentation are the anchors; secondary surveys are used for structure. Recently posted, lightly reviewed papers carry the `recent` tag and low-evidence items the `low-evidence` tag (see [decision 0004](../memories/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md)).
- Unverified third-party summaries are excluded; one example (Helix quantization and power claims) is recorded in [Figure Helix](../resources/figure-helix.md).

## Open questions
- No source provides a unified benchmark spanning accuracy, latency, energy and hardware for the techniques above; [technique comparison](technique-comparison.md) is the closest this wiki can offer.
