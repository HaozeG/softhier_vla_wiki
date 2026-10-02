---
type: concept
tags: [vla, architecture, history, action-head, dual-system]
sources: [resources/models/rt-2.md, resources/models/openvla.md, resources/models/octo.md, resources/models/pi0.md, resources/models/pi05.md, resources/models/fast-tokenizer.md, resources/models/openvla-oft.md, resources/models/gr00t-n1.md, resources/models/smolvla.md, resources/models/tinyvla.md, resources/models/figure-helix.md, resources/surveys/survey-vla-embodied-ai-ma.md, resources/compression/quantvla.md]
---
# VLA architecture overview

## Summary
(Terms such as prefix, KV cache and flow matching: glossary, [model and attention](../glossary/model-and-attention.md) and [action generation](../glossary/action-generation.md).)

Start with the [edge serving overview](vla-edge-serving-overview.md) for how this note fits the rest.

A vision-language-action (VLA) model maps camera images, a language instruction and (usually) robot state to robot actions using a pretrained vision-language model (VLM) as its core. Designs differ mostly in the **action head** (discrete tokens, parallel regression, diffusion/flow expert) and in how much of the VLM is kept. The trajectory from RT-2 (55B, cloud, 1–3 Hz) to SmolVLA (0.45B) is a move to smaller VLMs, fewer visual tokens, chunked continuous actions from a small expert, and asynchronous execution. Terminology follows [Ma et al.](../resources/surveys/survey-vla-embodied-ai-ma.md): VLA originated with RT-2, and models built on large VLMs are sometimes called "large VLAs".

## Diagram
```text
Pipeline (Octo is the exception: no VLM)

 images --> vision encoder --> projector -----+ visual tokens
   (SigLIP, or SigLIP + DINOv2)               |
 text -------------------------------- tokens +--> LM BACKBONE --> ACTION HEAD
 robot state ------------------------- tokens +

   LM backbone: whole, or cut (L = its number of LLM layers):
   SmolVLA keeps the first L/2 layers; GR00T N1 uses 12th-layer features

Axes: 1 how actions are decoded; 2 how a flow expert reads the backbone;
3 speeds

 axis 1  discrete tokens    nothing: the backbone emits 7-8 action tokens
                            itself (RT-2, OpenVLA)
 axis 1  parallel decoding  decoder outputs at empty action queries -> MLP
                            head (OpenVLA-OFT)
 axis 1  flow expert        refines a noisy chunk in steps (pi0, GR00T N1,
                            SmolVLA, Octo head)
 axis 2  flow: pi0          prefix and action tokens share one attention;
                            prefix keys and values cached
 axis 2  flow: GR00T N1     cross-attention to the VLM tokens
 axis 2  flow: SmolVLA      cross-attention to per-layer keys and values,
                            interleaved with self-attention
 axis 3  two speeds         slow VLM + fast policy (GR00T N1, Helix)
```

## Details
**Common pipeline.** Vision encoder (SigLIP, or fused SigLIP + DINOv2) → projector → language-model backbone over image, text and state tokens → action head. See [inference workload characterization](inference-workload-characterization.md) for how each stage loads hardware.

**Design axes** (numbered as in the diagram)
- **Axis 1, how actions are decoded:** discrete autoregressive tokens (RT-2, OpenVLA); parallel decoding with a regression head (OpenVLA-OFT); diffusion/flow expert (Octo head, π0, GR00T N1, SmolVLA). Details in [action representation and chunking](action-representation-and-chunking.md).
  - **DiT:** GR00T N1's action module is a DiT (diffusion transformer): a transformer that refines noisy actions, alternating cross-attention to the VLM tokens with self-attention over the noisy actions and state ([GR00T N1](../resources/models/gr00t-n1.md)); QuantVLA also calls such a head a DiT action head ([QuantVLA](../resources/compression/quantvla.md)).
- **Axis 2, how the flow expert reads the backbone (coupling of backbone and action expert):** shared self-attention with separate weights in π0 (a blockwise causal mask: images and language, then state, then noisy actions form three blocks, attention is bidirectional inside a block and earlier blocks cannot see later ones, so the prefix keys and values can be cached across flow steps, [π0](../resources/models/pi0.md)); cross-attention in GR00T N1; interleaved cross- and self-attention in SmolVLA.
- **Axis 3, two speeds:** a slow VLM plus a fast policy (GR00T N1, Helix); see [serving methods](serving-methods.md).

**Other differences between models**
- **Backbone size and depth:** from 55B (RT-2) and 7B (OpenVLA) to 2–3B (π0, GR00T N1) to 0.45B (SmolVLA, which keeps only the first half of the LLM layers) and TinyVLA's 0.4–1.3B.
- **Visual tokens:** 256 per 224×224 image for SigLIP-style encoders (OpenVLA, π0); 64 per frame in SmolVLA and GR00T N1, where pixel shuffle regroups neighbouring patch tokens into fewer, wider ones.
- **Where features are taken:** GR00T N1 uses the 12th LLM layer and reports faster inference and higher success than the last layer; SmolVLA uses layers up to N = L/2 (L is the number of LLM layers) as a speed trade-off: its ablation scores 78.5 at N = 16 against 80.3 at N = 32 on LIBERO (about 2 points lower), for half the layers ([layer skipping and pruning](layer-skipping-and-pruning.md)).
- **Training recipe:** π0.5 pretrains with discrete FAST tokens and post-trains a flow expert; TinyVLA and Octo skip large robot pretraining.

**Convergent efficient recipe (2025–2026):** small or truncated VLM, 64 visual tokens per frame, a small flow-matching expert with a handful of steps, chunked actions, and asynchronous execution. Each element has a measured or ablated justification in the linked notes: [layer skipping and pruning](layer-skipping-and-pruning.md), [token pruning and caching](token-pruning-and-caching.md), [flow-step reduction](flow-step-reduction.md), [serving methods](serving-methods.md).

## Reference models (skim)
The numbers in this table come from different papers and are not comparable. Octo is not VLM-based (see its [note](../resources/models/octo.md)); it is listed as the small-model reference point the others compare against, so the Summary's "VLM as its core" does not apply to it.

| Model                                     | Params                      | Backbone                             | Action head                          | Reported speed (hardware)                |
| ----------------------------------------- | --------------------------- | ------------------------------------ | ------------------------------------ | ---------------------------------------- |
| RT-2                                      | 5B / 12B / 55B              | PaLI-X / PaLM-E                      | 8 discrete tokens (256 bins)         | 5 Hz (5B), 1–3 Hz (55B), multi-TPU cloud |
| OpenVLA                                   | 7B                          | Prismatic (SigLIP + DINOv2, Llama 2) | 7 discrete tokens                    | about 6 Hz, RTX 4090, bf16, 15 GB        |
| [Octo](../resources/models/octo.md)       | 27M / 93M                   | T5 + patch CNN + transformer         | diffusion head, 20 steps             | not reported                             |
| π0                                        | 3.3B                        | PaliGemma 3B + 300M expert           | flow, 10 steps, H = 50               | 73 ms on-board RTX 4090, 3 cameras       |
| π0-FAST                                   | about 3B (no action expert) | PaliGemma                            | 30–60 FAST tokens                    | about 750 ms per chunk, RTX 4090         |
| OpenVLA-OFT                               | 7.5B                        | as OpenVLA                           | parallel L1 regression, K = 8–25     | 109.7 actions/s (K = 8, A100)            |
| GR00T N1                                  | 2.2B (1.34B VLM)            | Eagle-2 (SmolLM2 + SigLIP-2)         | DiT flow, 4 steps, H = 16            | 63.9 ms per chunk, L40, bf16             |
| SmolVLA                                   | 0.45B                       | truncated SmolVLM-2                  | flow expert (100M), 10 steps, n = 50 | see [SmolVLA](smolvla.md)                |
| [TinyVLA](../resources/models/tinyvla.md) | 0.42–1.3B                   | Pythia-based                         | diffusion head                       | 14 ms per action, A6000                  |
| Helix (S2 / S1)                           | 7B / 80M                    | open VLM / cross-attn transformer    | 200 Hz S1                            | S2 7–9 Hz, onboard embedded GPUs         |

In the table, Params is the model size in billions (B) or millions (M) of learned numbers (parameters). Speeds come from different hardware, batch sizes and definitions; do not rank models by this column. Per-paper detail (tables, ablations, limitations) lives in the `resources/` notes, for example [SmolVLA paper](../resources/models/smolvla.md) vs the model-centric [SmolVLA](smolvla.md) note; this note only compares designs across them.

## Open questions
- Whether discrete-token pretraining (π0.5, π0-FAST) or flow-only training is the better base for small models; the evidence here comes from PI's own comparisons.
- How much semantic generalization is lost when the VLM is truncated or replaced by a sub-1B model; most small-model results use LIBERO-style benchmarks and short tasks.
