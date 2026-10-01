---
type: paper
tags: [vla, foundational, discrete-actions, quantization, lora, open-source]
sources: [arxiv:2406.09246, https://arxiv.org/abs/2406.09246, https://openvla.github.io]
---
# OpenVLA: An Open-Source Vision-Language-Action Model

Kim, Pertsch, Karamcheti, et al. (Stanford, Berkeley, TRI, DeepMind, PI, MIT), arXiv 2406.09246 (v3, Sept 2024).

## Summary
OpenVLA is a 7B-parameter open VLA built from the Prismatic-7B VLM (fused SigLIP + DINOv2 encoders, 2-layer MLP projector, Llama 2 7B) and fine-tuned on 970k Open X-Embodiment episodes to predict discretized action tokens. It beats the 55B RT-2-X on the paper's evaluations and shows that LoRA fine-tuning and 4-bit quantization are viable on consumer GPUs.

## Key claims
- **Architecture (§3.1):** Prismatic-7B: about 600M-parameter fused vision encoder, MLP projector, Llama 2 7B. Single third-person image at 224×224 (384×384 gave no gain but took 3× longer to train, §3.4).
- **Action tokens (§3.2):** 256 bins per dimension, bin edges from the 1st–99th action quantiles; the 256 least-used Llama tokens are overwritten; 7-dimensional actions decoded autoregressively; cross-entropy on action tokens only.
- **Training (§3.4–3.5):** 27 epochs over the data; fixed LR 2e-5; vision encoder must be fine-tuned; 64 A100s for 14 days = 21,500 A100-hours, batch size 2048.
- **Headline result:** +16.5% absolute success over RT-2-X (55B) on 29 tasks with 7× fewer parameters; +20.4% over Diffusion Policy in multi-object language-grounded fine-tuning.
- **Inference (§3.5):** 15 GB in bf16, about 6 Hz on one RTX 4090 without compilation, speculative decoding or other tricks. A remote inference server is included.
- **LoRA (Table 1):** rank 32 gives 68.2% vs full fine-tuning 69.7% while training 1.4% of parameters (97.6M); about 8× less compute (10–15 h on one A100).
- **Quantization (Table 2, BridgeData V2, 8 tasks):** bf16 71.3% at 16.8 GB; int8 58.1% at 10.2 GB; int4 71.9% at 7.0 GB. int8 was slower (1.2 Hz on an A5000) because of dequantization overhead, and that slowdown, not token accuracy, caused the success drop; int4 ran at about 3 Hz on the A5000 (§5.4, footnote and Appendix D.4).
- **Limitations (§6):** single-image input; throughput too low for 50 Hz setups such as ALOHA; success typically under 90%. Authors suggest action chunking and speculative decoding.

## Relevance to SoftHier-VLA
OpenVLA is the canonical autoregressive baseline. Its int8-vs-int4 result is a concrete warning that weight quantization only helps when the kernel is memory-bound and dequantization is cheap; see [quantization](../../knowledge/quantization.md). Its speed limits motivated [OpenVLA-OFT](openvla-oft.md).

See also: [RT-2](rt-2.md), [OpenVLA-OFT](openvla-oft.md), [TinyVLA](tinyvla.md), [BitVLA](../compression/bitvla.md).
