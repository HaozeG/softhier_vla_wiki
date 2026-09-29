---
type: paper
tags: [quantization, ptq, w4a8, dit-action-head, pi0.5, gr00t]
sources: [arxiv:2602.20309, https://arxiv.org/abs/2602.20309]
---
# QuantVLA: Scale-Calibrated Post-Training Quantization for Vision-Language-Action Models

Zhang, Hsieh, Wan, Lin, Wang, Wang, Lei, Zhang (Ohio State, Michigan, CityU HK), arXiv 2602.20309 (v4, Apr 2026).

## Summary
QuantVLA claims to be the first post-training quantization framework for VLAs and the first to quantize a diffusion-transformer (DiT) action head. It applies W4A8 rotation-based quantization (DuQuant-style) to all LLM linear layers and the DiT MLPs, keeps DiT attention projections in floating point, and adds two calibration scalars to correct attention-temperature and residual-energy drift. It is evaluated on OpenPI π0.5 and GR00T N1.5 on LIBERO with A100 GPUs.

## Key claims
- **Selective layout (Table 1, no calibration):** quantizing only the LLM at W4A8 keeps π0.5 near baseline (96.5 vs 97.1). Quantizing the DiT alone gives 71.6, and LLM + full DiT gives 76.3. LLM + DiT MLP only gives 95.4. GR00T N1.5 shows the same ordering (86.5 FP16; 70.0 for LLM + full DiT).
- **Calibration (§3.3):** ATM rescales per-head attention logits (matches standard deviation to the FP teacher); OHB rescales per-layer output-projection energy (RMS match). Both are scalars folded into dequantization scales, so no extra operators at inference.
- **Main results (Table 2, LIBERO avg):** π0.5 FP16 97.1% at 4.27 GB (LLM+DiT) → QuantVLA W4A8 97.6% at 1.28 GB (70.0% savings). GR00T N1.5 86.5% at 2.02 GB → 88.0% at 0.91 GB (55.0%). Plain DuQuant on LLM+DiT: 76.3% and 70.0%.
- **Lower precision (Table 3):** π0.5 at W4A4 95.3%.
- **Non-DiT model (App. G):** OpenVLA W8A16 gets 86.0% vs 84.7% on LIBERO-Spatial; the DiT-specific calibration does not apply.
- **What is not shown:** the text read reports memory savings on the quantized components (LLM + DiT), not latency, and does not include the vision encoder. Small LIBERO suites and A100 GPUs only.

## Relevance to SoftHier-VLA
Shows that the flow/diffusion action head, run for many steps and accumulating error across them, is the most quantization-sensitive part, so a mixed-precision plan (LLM 4-bit weights, action head higher precision or MLP-only) is the safer default. See [quantization](../knowledge/quantization.md) and [flow-step reduction](../knowledge/flow-step-reduction.md).

See also: [BitVLA](bitvla.md), [vla.cpp](vla-cpp.md), [OpenVLA](openvla.md).
