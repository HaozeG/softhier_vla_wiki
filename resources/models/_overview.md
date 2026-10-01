---
covers: 887ba24cb2cc
---
# resources/models/

Model and architecture sources: the VLAs the wiki compares and the action representations they use.

- [FAST](fast-tokenizer.md) — DCT+BPE action tokens
- [Helix](figure-helix.md) — 7B S2 + 80M S1
- [Gemini On-Device](gemini-robotics-on-device.md) — product, no specs
- [GR00T N1](gr00t-n1.md) — dual-system 2.2B, 4-step DiT
- [Octo](octo.md) — 27–93M diffusion-head generalist policy
- [OpenVLA-OFT](openvla-oft.md) — parallel decoding + chunking, 26×
- [OpenVLA](openvla.md) — open 7B discrete-token VLA; LoRA, int4
- [π0](pi0.md) — PaliGemma + 300M flow expert; latency table
- [π0.5](pi05.md) — co-training, hierarchical inference
- [RT-2](rt-2.md) — first VLA; 55B cloud-served at 1–3 Hz
- [SmolVLA](smolvla.md) — 450M VLA, async inference
- [TinyVLA](tinyvla.md) — sub-1.5B, diffusion head
