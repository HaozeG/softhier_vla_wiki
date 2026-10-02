---
type: paper
tags: [vla, parallel-decoding, action-chunking, l1-regression, fine-tuning]
sources: [arxiv:2502.19645, https://arxiv.org/abs/2502.19645, https://openvla-oft.github.io]
---
# Fine-Tuning Vision-Language-Action Models: Optimizing Speed and Success (OpenVLA-OFT)

Kim, Finn, Liang (Stanford), arXiv 2502.19645 (v2, Apr 2025).

## Summary
Using OpenVLA as the base, the paper compares action decoding (autoregressive vs parallel), action representation (discrete vs continuous) and learning objective (next-token vs L1 regression vs diffusion). The winning recipe, OFT, combines parallel decoding with action chunking, continuous actions and an L1 loss. It lifts LIBERO success from 76.5% to 97.1% and raises action throughput 26× (43× on ALOHA with 25-step chunks).

## Key claims
- **Parallel decoding (§IV-B):** empty action embeddings plus bidirectional attention let one forward pass emit all D action dimensions; extending to chunk size K yields K·D actions in one pass.
- **Action head (§IV-B, App. B):** the decoder receives empty action embeddings (position only) with bidirectional attention, and a 4-layer ReLU MLP replaces the output embedding layer, mapping the final decoder layer's hidden states at those positions to continuous actions; the diffusion variant uses a 4-layer noise predictor of the same form with a DDIM sampler.
- **LIBERO efficiency (Table II, A100, 224×224 image; Hz = actions per second):** base OpenVLA 4.2 Hz, latency 0.2396 s; + parallel decoding 15.9 Hz, 0.0629 s; + chunking (K=8) 108.8 Hz, 0.0735 s; + L1 head 109.7 Hz; + wrist image and proprioception 71.4 Hz, 0.112 s.
- **LIBERO success (Table I):** OpenVLA 76.5 avg; + PD&AC 90.2; + continuous L1 95.3; full OFT with extra inputs 97.1, above π0 fine-tuned at 94.2.
- **Diffusion vs L1 (Table II):** "Hz" in Table II is throughput in actions per second (chunk K = 8 actions per call, so Hz = 8 / latency); latency is per chunk. Diffusion with 50 steps: 4.2 Hz (latency 1.907 s), 91.1% LIBERO-Long; 10 steps: 19.3 Hz (0.4145 s), 91.0%; 5 steps: 35.1 Hz (0.2279 s), 90.0%; 2 steps: 80.3 Hz (0.0996 s), 85.7%; 1 step: 109.4 Hz (0.0731 s), 0.0%. L1 regression matches diffusion at 109.7 Hz (0.0729 s). The 50-step diffusion head has the same throughput as base OpenVLA (4.2 Hz) but pauses 1.9 s between chunks.
- **ALOHA (Table III, 3 images, 14-D state, chunk 25, A100):** OpenVLA 1.8 Hz (0.543 s); OpenVLA-OFT+ 77.9 Hz (0.321 s); RDT-1B 84.1 Hz; Diffusion Policy 267.4 Hz; π0 291.6 Hz (JAX); ACT 432.8 Hz (0.058 s). FiLM on the vision transformer improves language grounding.
- **Related-work claim (§I):** FAST tokenization gives 2–13× speedups for autoregressive VLAs but with about 750 ms latency between chunks.
- **Limitations (§VIII):** L1 regression may struggle with truly multimodal demonstrations; untested for pretraining.

## Related
See also: [FAST](fast-tokenizer.md), [FlashVLA](../serving/flashvla-streaming.md), [LightVLA](../compression/lightvla.md), [VLA-Cache](../compression/vla-cache.md), [BitVLA](../compression/bitvla.md); all build on or compare against OFT.
