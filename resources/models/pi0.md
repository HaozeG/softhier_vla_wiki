---
type: paper
tags: [vla, foundational, flow-matching, action-expert, physical-intelligence]
sources: [arxiv:2410.24164, https://arxiv.org/abs/2410.24164, https://physicalintelligence.company/blog/pi0]
---
# π0: A Vision-Language-Action Flow Model for General Robot Control

Black, Brown, Driess, et al. (Physical Intelligence), arXiv 2410.24164 (v4, Jan 2026).

## Summary
π0 attaches a separate, smaller "action expert" (about 300M parameters) to a PaliGemma 3B VLM and generates continuous action chunks with conditional flow matching. It is trained on more than 10,000 hours of cross-embodiment data and controls dexterous robots at up to 50 Hz. It is the reference design for flow-matching VLAs, including [SmolVLA](smolvla.md).

## Key claims
- **Architecture (§IV, Appendix B):** one transformer with two weight sets (like a two-expert mixture): images and language use the PaliGemma weights (Gemma 2B: width 2048, depth 18, MLP dim 16,384, multi-query attention with 1 KV head, head dim 256); proprioceptive state and noisy actions use the action expert (width 1024, MLP dim 4096, about 300M). Total 3.3B parameters. Experts interact only through self-attention.
- **Attention mask:** blockwise causal with three blocks: [images, language], [state], [noisy actions]. Bidirectional inside a block; earlier blocks cannot attend to later ones, so prefix keys/values can be cached across flow steps.
- **Action chunk and flow:** H = 50 actions per chunk; flow-matching timestep is fused into the action embedding by an MLP; training samples τ from a beta distribution biased to noisy timesteps; inference uses forward Euler with 10 steps.
- **Inference (Appendix D, Table I, RTX 4090, 3 cameras):** image encoders 14 ms; observation forward pass 32 ms; 10 flow steps 27 ms; total 73 ms on-board, 86 ms off-board (13 ms network). Chunks are executed open-loop: inference every 0.8 s (16 actions) for the 20 Hz UR5e/Franka, every 0.5 s (25 actions) for the 50 Hz robots. Temporal ensembling hurt performance and was dropped.
- **Data (§V):** about 10,000 hours from 7 robot configurations and 68 tasks plus Open X-Embodiment (22 robots); open data is 9.1% of the mixture. Pre-train on broad data, then post-train on curated data.
- **Baselines:** π0-small (470M, no VLM initialisation), OpenVLA (cannot chunk) and Octo (93M) are all beaten on out-of-box tasks, and π0 beats them at compute parity.

## Relevance to SoftHier-VLA
π0's latency table is the most cited first-party breakdown, showing the vision, prefill and 10-step action loop split. See [inference workload characterization](../../knowledge/inference-workload-characterization.md) and [VLA architecture overview](../../knowledge/vla-architecture-overview.md). At 3.3B parameters it is above the size of a 10 TOPS-class deployment; see [edge hardware and the 10 TOPS gap](../../knowledge/edge-hardware-and-the-10-tops-gap.md).

Successor: [π0.5](pi05.md) keeps π0's architecture dimensions but pretrains with FAST tokens before adding the flow expert, and adds hierarchical subtask inference; π0 itself is flow-only and prompt-conditioned. Related: [FAST](fast-tokenizer.md), [GR00T N1](gr00t-n1.md), [OpenVLA](openvla.md).
