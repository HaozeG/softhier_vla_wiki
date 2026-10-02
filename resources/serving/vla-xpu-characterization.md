---
type: paper
tags: [characterization, npu, ascend, jetson, leaderboard, dp-cache, recent]
sources: [arxiv:2604.24447, https://arxiv.org/abs/2604.24447]
---
# Characterizing Vision-Language-Action Models across XPUs: Constraints and Acceleration for On-Robot Deployment

Zhou, Chen, Peng, Li, Li, Gu (Shanghai Jiao Tong University), arXiv 2604.24447 (Apr 2026, preprint).

## Summary
A cross-accelerator benchmark of VLA models (ACT, Diffusion Policy, SmolVLA, GR00T, π0, π0.5, OpenVLA) on RTX 4090, Jetson AGX Orin and Thor, Huawei Ascend 310B/310P NPUs, an Intel Arc B60 Pro and a CPU, ranked by cost, energy and time (CET). It profiles a compute-bound VLM phase followed by a memory-bound action-expert phase, and proposes two training-free accelerations, DP-Cache and V-AEFusion.

## Key claims
- **Hardware list (Table 10, BF16/FP16 TFLOP/s, memory, bandwidth):** Ascend 310B 10, 12 GB, 51.2 GB/s; Ascend 310P 88, 48 GB, 204.8 GB/s; Intel B60 Pro 90, 24 GB, 456 GB/s; AGX Orin 42, 64 GB, 204 GB/s; RTX 4090 330, 24 GB, 1000 GB/s; Jetson Thor 258, 128 GB, 273 GB/s. Thor and B60 numbers are the authors' estimate (half of INT8 TOPS).
- **Feasibility tiers (§3.1):** models above 1B parameters (GR00T, π0, π0.5, OpenVLA) need "Standard" or "Ultra" hardware; "Basic" hardware (an i7-11700 CPU, Ascend 310B) is limited to models like ACT, Diffusion Policy and SmolVLA. OpenVLA 7B does not fit the 12 GB Ascend 310B; swapping to disk on a CPU gives under 1 Hz.
- **π0 leaderboard (Table 1, baseline PyTorch):** RTX 4090 102.3 ms / 2.40 kJ; Thor 246.0 ms / 1.28 kJ; AGX Orin 920.6 ms / 1.87 kJ; Intel B60 306.5 ms / 6.36 kJ; Ascend 310P 818.0 ms / 2.62 kJ. Compiled (Table 3): 4090 35.2 ms (2.90×), Thor 163.0 ms (1.51×), 310P 350 ms (2.34×).
- **Finding 1:** parameter count does not predict speed. Diffusion Policy (100 denoising steps) is slower than π0 (4 steps in their setup).
- **Finding 3–4 (Fig. 5–6):** π0's VLM backbone reaches over 90% SM utilization while the action expert reaches 20–40% and takes about 2× the VLM's latency. Roofline: VLM decoder layer 185.1 GFLOP over 220 MB, about 840 FLOPs/byte; action expert about 64.5 FLOPs/byte, far below the ridge points (330 RTX 4090, 208 Orin, 945 Thor).
- **Existing accelerations on OpenVLA (Table 2):** 4-bit quantization 1.14× (avg success 76.5 → 67.7); cache 1.16×; speculative decoding 1.11×; spec + cache 1.29× (68.5); quant + cache 1.27× (65.1). Quantization lowers speculative-decoding acceptance.
- **DP-Cache (§5.2):** reuses diffusion features across a stable middle segment of denoising steps, found by offline profiling. On Diffusion Policy (RTX 4090): 378 → 181–200 ms (1.89–2.09×) with a small success change; on π0 1.29× with 0.6-point drop. V-AEFusion pipelines the VLM and action expert asynchronously.
- **Figure 2 (bar chart, log-scale inference frequency, read off the plot; approximate, roughly ±20%; values are not tabulated in the text):** ACT: i7 CPU about 13 Hz, Ascend 310B about 10.5 Hz, 310P about 70, B60 about 17, Orin about 40, Thor about 150, RTX 4090 about 330. SmolVLA: CPU about 0.3 Hz, 310P about 2, B60 about 3.8, Orin about 1.2, Thor about 4.9, RTX 4090 about 11; no 310B bar is shown. Diffusion Policy (100 steps): CPU about 0.15, 310P about 0.5, Orin about 0.2, RTX 4090 about 2.4. π0: 310P about 1.2, Orin about 1.05, Thor about 4.2, RTX 4090 about 9.8. So the only measured 10-TFLOP/s-class NPU result is ACT on the Ascend 310B; SmolVLA on the 310B is not plotted. Fig. 3 latency bars put SmolVLA at roughly 0.1 s on the RTX 4090 and about 0.8 s on Orin.
- **Headline claim:** up to 2.9× speedup on GPUs and 6× on edge NPUs (abstract); NPU detail was not in the parts read.
- **Caveats:** preprint; success rates reported are hardware-independent by construction (same precision); "π0 with 4 denoising steps" differs from the 10-step official setting.

## Related
See also: [edge bottleneck study](vla-edge-bottleneck-characterization.md), [VLA-Perf](vla-perf.md), [Jetson specs](../hardware/nvidia-jetson-platform-specs.md), [Sub-20-TOPS parts](../hardware/edge-accelerator-datasheets.md).
