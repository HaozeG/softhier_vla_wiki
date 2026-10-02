---
type: paper
tags: [cpu-inference, raspberry-pi, smolvla, act, int8, recent]
sources: [arxiv:2609.24274, https://arxiv.org/abs/2609.24274, https://vla-simd.github.io]
---
# vla.simd: Efficient CPU Inference for Language-Conditioned Manipulation

Nguyen, Truong, Le (VinRobotics, VinUniversity, TU Darmstadt), arXiv 2609.24274 (Sept 2026). Posted Sept 2026 and not yet independently reproduced; treat numbers as preliminary.

## Summary
A CPU inference engine (SIMD micro-kernels, per-process weight packing, per-episode caching of instruction-only tensors) evaluated on six policies and four CPUs, including a passively cooled Raspberry Pi 5. It introduces an "action-supply budget" for judging chunked policies on slow hardware and IMPACT, a 60M-parameter ACT-based policy with cached T5-small language conditioning.

## Key claims
- **Action-supply conditions (§III):** with query latency T_q, controller rate f_c, and available action window H: lagged execution needs d = ⌈f_c·T_q⌉ ≤ H (C1); time-aligned execution that discards stale actions needs 2d ≤ H (C2). f_eff = H/T_q is an action-supply rate, not a feedback rate.
- **Measured (Table III, fp32, median query, actions/s):** SmolVLA (450M, H = 50): Apple M4 73, i9-14900HX 42, Ryzen 5 5500 38, Raspberry Pi 5 6.1 (query latency 8.19 s). ACT (34M, H = 100): Pi 5 109 actions/s (0.92 s). Diffusion Policy (10 DDIM steps) Pi 5 6.3; 100 DDPM steps 0.8. Octo-Small Pi 5 7.8.
- **Only language-conditioned policy that meets 30 actions/s on a Pi 5:** IMPACT (33.5 fp32, 81.2 int8 after a 90 s thermal soak).
- **Versus compiled PyTorch:** median speedup about 1.4× (range 0.83–3.37×) over 28 policy-CPU pairs; fp32 numerical fidelity maintained (max abs difference ≤ 8.8e-5 in robot units).
- **W8A8 quantization (Table IV):** speedup over fp32 of 1.13–1.26× on desktop CPUs but 2.4–2.7× on the Pi 5 for ACT/IMPACT; on the M4 it slows Octo-Small and SmolVLA (0.66×, 0.71×).
- **Real robots:** SmolVLA served from an Apple M4 or a Ryzen on a UR10e: 12/20 successes each, with round-trip times 1177 and 2343 ms (about 0.5–1.0 s above engine latency due to transport).
- **Limitations (§VIII):** models up to 450M; no GPU, NPU, ONNX Runtime or OpenVINO comparison; medians rather than tails; one 90 s thermal soak; one LIBERO seed.

## Related
See also: [vla.cpp](vla-cpp.md), [SmolVLA](../models/smolvla.md), [LeRobot async docs](lerobot-async-inference-docs.md).
