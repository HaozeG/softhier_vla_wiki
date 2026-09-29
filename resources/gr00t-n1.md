---
type: paper
tags: [vla, dual-system, flow-matching, humanoid, nvidia]
sources: [arxiv:2503.14734, https://arxiv.org/abs/2503.14734]
---
# GR00T N1: An Open Foundation Model for Generalist Humanoid Robots

NVIDIA, arXiv 2503.14734 (v2, Mar 2025).

## Summary
GR00T N1 is a dual-system VLA. System 2 is the Eagle-2 VLM (SmolLM2 + SigLIP-2), which runs at about 10 Hz. System 1 is a diffusion transformer trained with flow matching that cross-attends to VLM features and emits action chunks at a higher rate. The public GR00T-N1-2B has 2.2B parameters, 1.34B of them in the VLM. Training mixes real robot data, human video with latent actions, and synthetic simulation and video-generated trajectories.

## Key claims
- **Sizes and speed (§2, Fig. 1):** 2.2B parameters total; 1.34B in the VLM. Sampling a 16-action chunk takes 63.9 ms on an L40 GPU in bf16. System 2 runs at 10 Hz on an L40; System 1 generates closed-loop actions at 120 Hz.
- **Image tokens (§2.1):** 224×224 images, pixel shuffle, 64 image tokens per frame.
- **Middle-layer features (§2.1):** using the 12th LLM layer instead of the last gave faster inference and higher downstream success for GR00T-N1-2B.
- **Action module (§2.1):** DiT with alternating cross-attention (to VLM tokens) and self-attention (over noisy actions and state). Embodiment-specific MLPs encode state and action; chunk H = 16; K = 4 Euler denoising steps "worked well across all embodiments".
- **Cross-attention instead of shared self-attention (§5):** contrasted with π0's mixture-of-experts style, cross-attention leaves freedom to choose the VLM and action-module architectures independently.
- **Data pyramid (§2.2, §3):** web and human video at the base; synthetic simulation and neural-video trajectories in the middle (in-house teleoperation grown about 10× from 88 to 827 hours with generated neural trajectories); real robot data at the top. Latent actions from a VQ-VAE inverse-dynamics model label action-free videos.
- **Limitations (§4.6):** short-horizon tabletop manipulation; synthetic data quality and diversity.

## Relevance to SoftHier-VLA
GR00T N1 is a second data point (after [SmolVLA](smolvla.md)) for "middle-layer VLM features plus 64 tokens per frame plus few-step flow" as the efficient recipe. Its dual-system split is the design analysed in [serving methods](../knowledge/serving-methods.md) and in [VLA-Perf](vla-perf.md).

See also: [π0](pi0.md), [π0.5](pi05.md), [Octo](octo.md), [SmolVLA](smolvla.md).
