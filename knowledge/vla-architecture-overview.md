---
type: concept
tags: [vla, architecture, history, action-head, dual-system]
sources: [resources/rt-2.md, resources/openvla.md, resources/octo.md, resources/pi0.md, resources/pi05.md, resources/fast-tokenizer.md, resources/openvla-oft.md, resources/gr00t-n1.md, resources/smolvla.md, resources/tinyvla.md, resources/figure-helix.md, resources/survey-vla-embodied-ai-ma.md]
---
# VLA architecture overview

## Summary
Start with the [edge serving overview](vla-edge-serving-overview.md) for how this note fits the rest.

A vision-language-action (VLA) model maps camera images, a language instruction and (usually) robot state to robot actions using a pretrained vision-language model (VLM) as its core. Designs differ mostly in the **action head** (discrete tokens, parallel regression, diffusion/flow expert) and in how much of the VLM is kept. The trajectory from RT-2 (55B, cloud, 1–3 Hz) to SmolVLA (0.45B) is a move to smaller VLMs, fewer visual tokens, chunked continuous actions from a small expert, and asynchronous execution. Terminology follows [Ma et al.](../resources/survey-vla-embodied-ai-ma.md): VLA originated with RT-2, and models built on large VLMs are sometimes called "large VLAs".

## Details
**Common pipeline.** Vision encoder (SigLIP, or fused SigLIP + DINOv2) → projector → language-model backbone over image, text and state tokens → action head. See [inference workload characterization](inference-workload-characterization.md) for how each stage loads hardware.

**Design axes**
- **Action decoding:** discrete autoregressive tokens (RT-2, OpenVLA); parallel decoding with a regression head (OpenVLA-OFT); diffusion/flow expert (Octo head, π0, GR00T N1, SmolVLA); two-speed systems (GR00T N1, Helix). Details in [action representation and chunking](action-representation-and-chunking.md).
- **Backbone size and depth:** from 55B (RT-2) and 7B (OpenVLA) to 2–3B (π0, GR00T N1) to 0.45B (SmolVLA, which keeps only the first half of the LLM layers) and TinyVLA's 0.4–1.3B.
- **Visual tokens:** 256 per 224×224 image for SigLIP-style encoders (OpenVLA, π0); 64 per frame with pixel shuffle in SmolVLA and GR00T N1.
- **Coupling of backbone and action expert:** shared self-attention with separate weights in π0 (blockwise causal mask, prefix KV cached across flow steps); cross-attention in GR00T N1; interleaved cross- and self-attention in SmolVLA.
- **Where features are taken:** GR00T N1 uses the 12th LLM layer; SmolVLA uses layers up to N = L/2; both report better or equal accuracy and faster inference than the last layer.
- **Training recipe:** π0.5 pretrains with discrete FAST tokens and post-trains a flow expert; TinyVLA and Octo skip large robot pretraining.

**Reference models**

| Model | Params | Backbone | Action head | Reported speed (hardware) |
|---|---|---|---|---|
| RT-2 | 5B / 12B / 55B | PaLI-X / PaLM-E | 8 discrete tokens (256 bins) | 5 Hz (5B), 1–3 Hz (55B), multi-TPU cloud |
| OpenVLA | 7B | Prismatic (SigLIP + DINOv2, Llama 2) | 7 discrete tokens | about 6 Hz, RTX 4090, bf16, 15 GB |
| [Octo](../resources/octo.md) | 27M / 93M | T5 + patch CNN + transformer | diffusion head, 20 steps | not reported |
| π0 | 3.3B | PaliGemma 3B + 300M expert | flow, 10 steps, H = 50 | 73 ms on-board RTX 4090, 3 cameras |
| π0-FAST | about 3B (no action expert) | PaliGemma | 30–60 FAST tokens | about 750 ms per chunk, RTX 4090 |
| OpenVLA-OFT | 7.5B | as OpenVLA | parallel L1 regression, K = 8–25 | 109.7 Hz (K = 8, A100) |
| GR00T N1 | 2.2B (1.34B VLM) | Eagle-2 (SmolLM2 + SigLIP-2) | DiT flow, 4 steps, H = 16 | 63.9 ms per chunk, L40, bf16 |
| SmolVLA | 0.45B | truncated SmolVLM-2 | flow expert (100M), 10 steps, n = 50 | see [SmolVLA](smolvla.md) |
| [TinyVLA](../resources/tinyvla.md) | 0.42–1.3B | Pythia-based | diffusion head | 14 ms per action, A6000 |
| Helix (S2 / S1) | 7B / 80M | open VLM / cross-attn transformer | 200 Hz S1 | S2 7–9 Hz, onboard embedded GPUs |

Speeds come from different hardware, batch sizes and definitions; do not rank models by this column. Per-paper detail (tables, ablations, limitations) lives in the `resources/` notes, for example [SmolVLA paper](../resources/smolvla.md) vs the model-centric [SmolVLA](smolvla.md) note; this note only compares designs across them.

**Convergent efficient recipe (2025–2026):** small or truncated VLM, 64 visual tokens per frame, a small flow-matching expert with a handful of steps, chunked actions, and asynchronous execution. Each element has a measured or ablated justification in the linked notes: [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [flow-step reduction](flow-step-reduction.md), [serving methods](serving-methods.md).

## Open questions
- Whether discrete-token pretraining (π0.5, π0-FAST) or flow-only training is the better base for small models; the evidence here comes from PI's own comparisons.
- How much semantic generalization is lost when the VLM is truncated or replaced by a sub-1B model; most small-model results use LIBERO-style benchmarks and short tasks.
