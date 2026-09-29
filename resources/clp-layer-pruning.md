---
type: paper
tags: [layer-pruning, cka, pi0, gr00t, smolvla, finetuning, recent]
sources: [arxiv:2606.20246, https://arxiv.org/abs/2606.20246, https://clpvla.github.io/]
---
# Finetuning Vision-Language-Action Models Requires Fewer Layers Than You Think (CLP)

Nguyen, Ho, Ha, et al. (VinUniversity, VinRobotics, and others), arXiv 2606.20246 (v2, Jun 2026). Recent paper.

## Summary
CKA-guided Layer Pruning (CLP) removes redundant transformer layers from a pretrained flow-matching VLA before fine-tuning, using one forward pass over a calibration set. Consecutive layers with high centered kernel alignment form blocks; the first layer of each block is kept and the rest are candidates for removal. The result is a statically smaller model (no routers, no extra loss) that trains and runs faster.

## Key claims
- **Method (§4, Alg. 1):** compute CKA between consecutive layers' hidden states over calibration data; group layers with similarity ≥ τ into blocks; keep each block's anchor layer; remove the top-k most redundant others. Applied separately to the VLM and to the action head.
- **Layers removed (Table 5):** GR00T-N1.5: 5 of 12 VLM layers, 3 of 4 VL self-attention layers, 8 of 16 DiT layers; SmolVLA: 10 layers (VLM and expert together, from 16); π0: 12 layers across VLM and expert (as listed).
- **Efficiency (Table 1, RTX 4070, LIBERO):** π0 3.5B → 2.7B, inference 211 → 152 ms (−27.9%), GFLOPs 3073 → 2197, training 15.5 → 11.2 h; GR00T-N1.5 2.7B → 2B, 121 → 85 ms, GFLOPs 1010 → 512 (−49.3%), training 10.7 → 7.4 h; SmolVLA 450M → 354M, 201 → 137 ms (−31.8%), GFLOPs 598 → 536, training 24.75 → 8.83 h.
- **Accuracy (Table 2, LIBERO):** π0 94.6 → 93.9 avg (1.39×); GR00T-N1.5 93.9 → 93.0 (1.42×); SmolVLA 77.15 → 76.75 (1.47×). Performance is flat up to about 50% layer pruning on π0 (LIBERO) and GR00T-N1.5 (RoboCasa), Fig. 3.
- **Low-data effect:** with 10% of LIBERO data, π0 rises from 77.7% to 84.6% after pruning (MoLe-VLA dynamic skipping: 79.7%), which the authors attribute to regularization. Real world (10 tasks, four embodiments): GR00T-N1.5 73.5% → 75.9%, up to 1.94× faster fine-tuning.
- **Alternatives compared (Fig. 3d):** CKA selection beat MSE, cosine, random and "keep first layers" selection.
- **Limitations (§7):** a global criterion that ignores modality-specific token dynamics; studied only for post-pretraining fine-tuning, not pretraining.
- **Caveat:** SmolVLA's baseline here (77.15% on LIBERO) is far below the 87.3% the SmolVLA paper reports for the 0.45B model (88.75% is the 2.25B variant), so comparisons across papers need the same training and evaluation protocol.

## Relevance to SoftHier-VLA
A static, hardware-friendly compression (fewer layers, same shapes) for the models this wiki cares about, including SmolVLA. Because the pruning happens before fine-tuning, it changes the model you deploy, not the run-time control flow. See [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md); compare [pruned-VLA recovery](pruned-vla-recovery.md) (width vs depth).

See also: [EfficientVLA](efficientvla.md), [DeeR-VLA](deer-vla.md), [DySL-VLA](dysl-vla.md), [SmolVLA](smolvla.md).
