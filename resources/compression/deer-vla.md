---
type: paper
tags: [early-exit, dynamic-inference, layer-skipping, calvin, roboflamingo]
sources: [arxiv:2411.02359, https://arxiv.org/abs/2411.02359, https://github.com/yueyang130/DeeR-VLA]
---
# DeeR-VLA: Dynamic Inference of Multimodal Large Language Models for Efficient Robot Execution

Yue, Wang, Kang, Han, Wang, Song, Feng, Huang (Tsinghua, ByteDance), arXiv 2411.02359 (NeurIPS 2024).

## Summary
DeeR adds intermediate exits to the LLM of a robot MLLM (OpenFlamingo-based RoboFlamingo++), so that easy situations use a shallow prefix of the LLM and hard ones use more layers. The exit rule is action consistency between adjacent exits, with thresholds solved from average-FLOPs, peak-FLOPs or GPU-memory budgets. On CALVIN it cuts LLM compute by 5.2–6.5× and LLM memory 2–6× at similar task length.

## Key claims
- **Motivation (Table 1):** RoboFlamingo++ with 24 / 12 / 6 LLM layers costs 31.2 / 15.6 / 7.8 GFLOPs per action and succeeds 78.9 / 78.0 / 75.7%.
- **Architecture (§3.1, App. A):** exits after every two self-attention layers; only the first 12 of 24 (3B) or 32 (9B) LLM layers are used, giving 6 exits. Max-pooled features feed a 4-layer LSTM plus MLP action head. Each 3B LLM layer is about 0.5 GB and 1.3 GFLOPs at batch 1; each 9B layer about 1.0 GB and 2.85 GFLOPs.
- **Exit criterion (§3.2):** exit at the smallest i where ‖π(x̃ⁱ) − π(x̃ⁱ⁻¹)‖₂ < ηᵢ. Compared with feature-similarity and time-based schedules, action consistency wins at equal GFLOPs (Table 4).
- **Training (§3.3):** random sampling over exits plus auxiliary action heads; without the auxiliary losses ABCD→D length falls (Table 3).
- **Results (Fig. 3–4):** 3B: LLM FLOPs 5.2–6.5× lower, peak FLOPs 2× lower, LLM memory 2–6× lower (DeeR-S uses about 2 GB). 9B: 1.8–5.7× lower compute, 12 GB vs 32 GB for RoboFlamingo 9B.
- **Wall-clock (Table 5, V100, ABCD→D):** avg length 4.07 vs 4.08; GFLOPs 31.2 → 6.0; LLM time 55 ms → 17.5 ms (−68.1%, versus −80.7% theoretical FLOPs). No code optimization for early exit.
- **Quantization (Table 6):** float32 6 GB / len 4.13; float16 3 GB / 4.12; int4 1.7 GB / 3.91.
- **Limitations (§5):** simulation only; counts only LLM cost while the vision encoder is also significant.

## Related
See also: [DySL-VLA](dysl-vla.md), [vla.cpp](../serving/vla-cpp.md), [Guan et al.](../surveys/survey-efficient-vla-guan.md).
