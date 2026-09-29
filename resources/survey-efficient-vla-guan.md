---
type: paper
tags: [survey, efficient-vla, token-pruning, layer-skipping, quantization]
sources: [arxiv:2510.17111, https://arxiv.org/abs/2510.17111]
---
# Efficient Vision-Language-Action Models for Embodied Manipulation: A Systematic Survey

Guan, Hu, Li, Cheng (CAS Institute of Automation), arXiv 2510.17111 (v3, Oct 2025).

## Summary
A survey of VLA efficiency organized along the inference pipeline: model architecture (static backbones, dynamic computation pathways, dual-system), perception features (spatial token selection and temporal reuse), action generation (raw vs reasoning-based actions), and training/inference strategies (PEFT, distillation, pruning, quantization, parallel decoding). It frames efficiency in terms of latency, memory footprint, and training/inference cost on edge platforms such as mobile manipulators.

## Key claims
- **Backbones (§3.1):** first-generation VLAs were huge (RT-2 at 55B parameters, about 3 Hz). Most latency comes from the language model, so newer work downsizes it: TinyVLA (Pythia-1.3B), RoboMamba (Mamba, about 2.7B), SmolVLA (SmolVLM-2 0.24B/0.45B/2.25B with last layers removed), NORA (Qwen-2.5-VL-3B).
- **Dynamic pathways (§3.2):** static layer removal (SmolVLA, FLOWER prunes upper layers because they over-specialize on next-token prediction); early exit (DeeR-VLA, with heads at intermediate layers and a similarity-based exit criterion tuned against FLOPs/memory); layer-as-expert routing with self-distillation (MoLE-VLA, arguing deep features still matter).
- **Token pruning (§4.1):** FastV (top-K by average attention), EfficientVLA (instruction-relevance plus diversity), SP-VLA (adds spatial/contour cues, adaptive to motion), FlashVLA-SVD (an Information Contribution Score from SVD, because attention scores are not exposed by FlashAttention), LightVLA (query-driven differentiable selection with Gumbel-softmax on encoder outputs), ADP (two-stage pruning).
- **Training-time compression (§6.1):** LoRA/PEFT (TinyVLA), distillation (CEED-VLA consistency distillation, MoLE-VLA self-distillation, VITA-VLA), GLUESTICK (training-free low-rank recovery for pruned weights), SQIL (state-importance-guided QAT), BitVLA (ultra-low-bit QAT; memory from about 15.1 GB for OpenVLA to about 1.4 GB).
- **Inference (§6.2):** autoregressive decoding is sequential; diffusion needs many denoising steps. Parallel/NAR alternatives: OpenVLA-OFT (bidirectional attention, continuous L1 regression), Spec-VLA (relaxed speculative decoding), PD-VLA (Jacobi), CEED-VLA (consistency distillation and early exit).
- **Cloud-edge partitioning (§3):** future designs should consider lightweight fast subsystems locally and heavy reasoning in the cloud, accounting for latency, bandwidth and privacy.
- **Stated gap (§6.3):** most VLA efficiency methods are borrowed from VLM work and rarely address robotics-specific needs (temporal consistency, execution latency).

## Relevance to SoftHier-VLA
Cross-check for [VLA efficiency taxonomy](../knowledge/vla-efficiency-taxonomy.md). Complements [Yu et al.](survey-efficient-vla-yu.md); the two overlap heavily, so cite primary papers for any number. Its claim that most latency sits in the LLM is refined by [VLA-Perf](vla-perf.md), which shows the action expert dominating on Jetson Thor for π0.

See also: [Yu et al.](survey-efficient-vla-yu.md), [Ma et al.](survey-vla-embodied-ai-ma.md), [Zhong et al.](survey-vla-action-tokenization.md).
