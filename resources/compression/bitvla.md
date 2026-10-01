---
type: paper
tags: [quantization, 1-bit, ternary, bitnet, qat, openvla-oft]
sources: [arxiv:2506.07530, https://arxiv.org/abs/2506.07530, https://github.com/ustcwhy/BitVLA]
---
# BitVLA: 1-bit Vision-Language-Action Models for Robotics Manipulation

Wang, Xiong, Wang, Chen (ICT, Chinese Academy of Sciences), arXiv 2506.07530 (v2, Mar 2026).

## Summary
BitVLA is a natively ternary ({−1, 0, +1}) VLA built on the BitNet b1.58 2B4T LLM with a SigLIP-L vision encoder. A "quantize-then-distill" stage compresses the vision encoder to 1.58-bit weights with INT8 activations, guided by a full-precision teacher. With OpenVLA-OFT-style parallel decoding and an L1 head it reaches LIBERO accuracy near OpenVLA-OFT at 1.4 GB of model memory.

## Key claims
- **Architecture (§III-A):** BitNet b1.58 2B4T LLM, SigLIP-L at 224×224 (256 visual tokens), two-layer MLP connector kept in full precision, action head full precision; total 3.0B. Weights quantized by absmean to ternary; activations by per-token absmax to INT8; inference uses a BitBLAS custom kernel. Causal attention kept, because a bidirectional mask hurt real-world performance.
- **Training (§III-B, §IV-A):** three stages: multimodal training, quantize-then-distill (5M-sample subset, up to 10B tokens, alignment loss weight 0.1), then robotics pretraining on about 1M Open X-Embodiment samples (200K steps, batch 2048). Cost: 7 days on 8 H800 for the VLM stages plus 14 days on 16 H800 for robotics pretraining.
- **LIBERO (Table I):** BitVLA 96.0% avg at 1.4 GB vs OpenVLA-OFT 97.1% at 15.4 GB (11×), π0 94.2% at 7.0 GB, SmolVLA 88.8% at 4.6 GB. Without robotics pretraining 94.8%.
- **PTQ baselines (Table II):** OpenVLA-OFT INT8 96.7% at 7.7 GB; INT4 96.9% at 4.7 GB. OpenVLA INT4 72.7% at 4.4 GB (from 76.5%).
- **Vision encoder (Table III):** 1.58-bit ViT uses 0.1 GB vs 0.8 GB, with a 1.5-point drop in average VQA accuracy (53.0 → 51.5). Without the alignment loss the average falls to 42.4.
- **Efficiency (Fig. 6):** on an A100 with three 224×224 images, chunk 25: latency 73 ms and 341.1 Hz vs OpenVLA-OFT+ 321 ms / 77.9 Hz (4.4×). The baseline numbers are copied from the [OpenVLA-OFT](../models/openvla-oft.md) paper, not re-measured.
- **Real world (Fig. 4–5):** competitive on out-of-distribution tasks, but near-zero success without robotics pretraining.
- **Limitations (§VI):** needs quantization-aware training (not a drop-in conversion of an existing FP backbone); pretraining scale is small (about 1M samples).
- **Energy argument (§VI):** ternary-by-INT8 linear layers reduce to integer additions, so the authors argue for dedicated 1-bit VLA accelerators. Not measured.

## Relevance to SoftHier-VLA
The only work here that directly motivates custom low-bit datapaths: a ternary×INT8 multiply-accumulate needs no multipliers. Latency gains depend on a specialised kernel; on a generic accelerator without ternary support the benefit would be memory only. See [quantization](../../knowledge/quantization.md).

See also: [OpenVLA](../models/openvla.md), [OpenVLA-OFT](../models/openvla-oft.md), [vla.cpp](../serving/vla-cpp.md) (ternary kernels), [QuantVLA](quantvla.md).
