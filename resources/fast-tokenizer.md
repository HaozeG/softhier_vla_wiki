---
type: paper
tags: [action-tokenization, dct, autoregressive, pi0-fast, physical-intelligence]
sources: [arxiv:2501.09747, https://arxiv.org/abs/2501.09747, https://pi.website/research/fast]
---
# FAST: Efficient Action Tokenization for Vision-Language-Action Models

Pertsch, Stachowicz, Ichter, Driess, Nair, Vuong, Mees, Finn, Levine (Physical Intelligence, Berkeley, Stanford), arXiv 2501.09747 (Jan 2025).

## Summary
FAST compresses an action chunk with a discrete cosine transform per dimension, quantizes and flattens the coefficients, then applies byte-pair encoding, yielding far fewer tokens than per-step binning. This makes autoregressive VLAs trainable on high-frequency dexterous data. π0-FAST matches diffusion π0 quality with up to 5× less training compute, but decodes autoregressively and is much slower at inference.

## Key claims
- **Why binning fails (§IV):** with per-timestep bins, consecutive tokens are highly correlated at high control rates, so next-token loss can be minimized by copying the previous token (toy interpolation study, Fig. 3).
- **Algorithm (§V):** normalize by 1st–99th quantile; DCT per dimension; scale-and-round (a scale γ trades compression against fidelity); flatten low frequency first; BPE. FAST+ is a universal tokenizer trained on 1M real action trajectories.
- **Token counts per 1-second chunk (Table I):** BridgeV2 (7-D, 5 Hz) 35 → 20; DROID (7-D, 15 Hz) 105 → 29; bussing (7-D, 20 Hz) 140 → 28; shirt folding (14-D, 50 Hz) 700 → 53. FAST yields roughly 30 tokens per arm per chunk regardless of frequency.
- **Training efficiency (§VI-F):** π0-FAST matches diffusion π0 across generalist tasks (including laundry folding) with about 5× fewer GPU hours; on the large bussing dataset it reaches high performance with 3× fewer steps.
- **Inference cost (§VI-E):** diffusion π0 predicts a 1 s chunk in about 100 ms on an RTX 4090; π0-FAST needs about 750 ms because it decodes 30–60 tokens through the 2B LLM instead of 10 steps through a 300M expert. The authors defer speculative decoding, quantization and custom kernels to future work.

## Relevance to SoftHier-VLA
FAST is the reason π0.5 is pretrained with discrete tokens and then switched to a flow-matching expert for inference: cheap training, cheap serving ([π0.5](pi05.md)). For a serving accelerator the take-away is that autoregressive action decoding is dominated by memory-bound decode passes over the full LLM. See [action representation and chunking](../knowledge/action-representation-and-chunking.md).

See also: [OpenVLA](openvla.md), [π0](pi0.md), [OpenVLA-OFT](openvla-oft.md), [Zhong et al.](survey-vla-action-tokenization.md).
