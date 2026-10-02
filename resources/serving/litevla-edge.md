---
type: paper
tags: [edge, llama-cpp, gguf, jetson, smolvlm, low-evidence]
sources: [arxiv:2603.03380, https://arxiv.org/abs/2603.03380]
---
# LiteVLA-Edge: Quantized On-Device Multimodal Control for Embedded Robotics

Williams, Gupta, George, Sarkar (Clark Atlanta University, Siemens), arXiv 2603.03380 (Mar 2026). Low-evidence source: latency only, no task success.

## Summary
Fine-tunes a distilled SmolVLM-256M backbone to emit discrete velocity-command tokens, quantizes to 4-bit GGUF (Q4_K_M) and runs it through llama.cpp on a Jetson Orin, reporting a mean end-to-end latency of 150.5 ms (about 6.6 Hz) inside a ROS 2 pipeline. The paper scopes its claims to deployability and timing feasibility.

## Key claims
- **Setup (§IV):** LoRA (rank 8) fine-tuning in FP32, Q4_K_M GGUF, all 42 layers offloaded to the GPU via CUDA, context length 512, at most 12 output tokens; 256M parameters; ROS 2 bridge publishing Twist commands.
- **Latency (§V, Table II):** mean 150.5 ms, standard deviation about 0.13 ms over 300 runs; 6.64 Hz reasoning frequency; low-level controller runs at 100 Hz separately.
- **Inconsistency in the paper:** the text and title say Jetson AGX Orin (64 GB) but Table II and §V-D say Jetson Orin NX, and the power mode is not stated. The "closed-loop evaluation" is a simulated frame sequence, not task success.
- **Comparison table (Table I):** lists OpenVLA (about 5 Hz, RTX 4090) and EdgeVLA (about 10 Hz, A100) but the paper itself notes cross-paper comparisons are not like-for-like.
- **Prior work by the same group:** "Lite VLA" ran on a Raspberry Pi 4 with multi-second to multi-minute inference (as cited in [vla.simd](vla-simd.md)).

## Related
See also: [vla.cpp](vla-cpp.md), [vla.simd](vla-simd.md), [SmolVLA](../models/smolvla.md).
