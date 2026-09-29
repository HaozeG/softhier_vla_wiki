---
type: paper
tags: [vla, foundational, discrete-actions, cloud-serving, google]
sources: [arxiv:2307.15818, https://arxiv.org/abs/2307.15818]
---
# RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control

Brohan et al. (Google DeepMind), arXiv 2307.15818 (July 2023; CoRL 2023). The paper that coined "vision-language-action (VLA) model".

## Summary
RT-2 co-fine-tunes large pretrained VLMs (PaLI-X 5B/55B, PaLM-E 12B) on web vision-language data plus robot trajectories, expressing robot actions as text tokens. This yields policies with better generalization to novel objects and backgrounds and some emergent reasoning. Because the models are huge, they are served from a multi-TPU cloud service rather than on the robot.

## Key claims
- **Action tokenization (§3.2):** end-effector displacement (6 DoF), gripper extension and a termination flag; each continuous dimension is discretized into 256 bins, giving 8 integers per action, emitted as a string. For PaLI-X, integers up to 1000 already have tokens; for PaLM-E the 256 least-used tokens are overwritten. Output is constrained to valid action tokens during decoding.
- **Co-fine-tuning (§3.2, §4.3):** mixing robot data (about 50% of the RT-2-PaLI-X mixture) with original web data beats robot-only fine-tuning, which beats training from scratch (Table 6: 5B co-fine-tune 44 vs fine-tune 42 vs scratch 9 avg; 55B co-fine-tune 63 vs fine-tune 52).
- **Serving (§3.3):** the largest model, 55B, cannot run on desktop or on-robot GPUs; it is deployed in a multi-TPU cloud service queried over the network at about 1–3 Hz. The 5B variant runs at about 5 Hz. One service can serve multiple robots.
- **Baseline scale:** RT-1 is a 35M-parameter transformer; on seen tasks RT-2 is similar to RT-1, and generalization is about 2× better than RT-1 and MOO (§4.1).
- **Chain of thought (§4.4):** adding a natural-language "Plan" before the action tokens (fine-tuned for a few hundred steps) gives qualitative multi-stage reasoning.
- **Limitations (§5):** the robot gains no new motion skills beyond the robot data; real-time inference is a bottleneck for high-frequency control; the authors name quantization and distillation as directions for lower-cost hardware.

## Relevance to SoftHier-VLA
RT-2 defines the first generation of VLA serving: cloud inference at low Hz. It is the historical origin of the discrete-token action design described in [VLA architecture overview](../knowledge/vla-architecture-overview.md) and [action representation and chunking](../knowledge/action-representation-and-chunking.md).

See also: [OpenVLA](openvla.md), [Octo](octo.md), [Ma et al.](survey-vla-embodied-ai-ma.md).
