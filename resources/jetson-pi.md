---
type: paper
tags: [edge, jetson-orin, jetson-thor, async-inference, pi0.5, recent]
sources: [arxiv:2607.12659, https://arxiv.org/abs/2607.12659, https://github.com/PKU-SEC-Lab/Jetson-PI]
---
# Jetson-PI: Towards Onboard Real-Time Robot Control via Foresight-Aligned Asynchronous Inference

Yang, Wang, Wang, Guo, Yu, Liu, Xu, Dong, Li (Peking University, AIRS, PrimeBot), arXiv 2607.12659 (v5, Sept 2026). Recent paper; treat as not yet widely reviewed.

## Summary
Jetson-PI targets π0/π0.5-style VLAs on low-power Jetson Orin and Thor. It combines (1) a 40M-parameter future-correction module that predicts the VLM's final-layer state after the committed actions, so the action expert can predict from the future time step; (2) confidence-based scheduling that calls the VLM once and the action expert several times; and (3) a llama.cpp-based engine with CUDA-graph reuse, GPU-resident buffers and flow unrolling. It also gives one of the few measured latency breakdowns for a 3B-class VLA on Jetson hardware.

## Key claims
- **Measured π0.5 latency (Table 1, ms):** Jetson Orin 30 W: ViT 329.0, LLM 858.2, action expert 1102.2, total 2289.4. Orin 50 W: 152.3 / 631.0 / 536.8 / 1420.8 (about 0.7 Hz). Thor: 61.7 / 187.0 / 209.2 / 457.9. RTX A6000: 128.2. RTX 4090: 76.4. π0 is similar (Orin 50 W 1403.0 ms, Thor 447.9 ms). The exact Orin module is not stated in the text read; the 30 W / 50 W modes suggest an AGX-class part.
- **Power motivation (Fig. 1):** with a 500 Wh battery pack, an RTX 4090 cuts robot battery life by up to 6.0× compared with Jetson Orin.
- **Two async failure modes (§3):** perception-execution misalignment (grows with latency Δ) and long reaction time (between Δ and Δ + L action steps, where Δ is the inference latency in action steps and L the number of actions executed per chunk; the paper's LIBERO setup uses chunk size H = 20 with L = H − Δ). Naive async, RTC and VLASH degrade as Δ grows (Fig. 3, Table 3).
- **Method (§4):** the correction module takes the Q-Former-compressed final VLM state at t plus the committed actions and predicts the compressed state at t + Δ (about 1% of model parameters). A confidence output decides when to re-invoke the VLM.
- **System stack (Table 4, π0.5):** Orin: naive 1420.8 ms / 0.70 Hz → scheduling 1.48 Hz → CUDA-graph reuse total 476.1 ms, 4.41 Hz → buffering + flow unrolling total 412.9 ms, reaction 165.1 ms, 6.06 Hz. Thor: 457.9 ms → 309.5 ms total, 2.18 → 7.59 Hz. Reported gains: 8.66× (Orin) and 3.48× (Thor) in control frequency vs naive PyTorch; 5.41× vs vla.cpp (893 ms on Orin).
- **LIBERO (Table 3, π0.5):** averaged over delays, +14.8% over VLASH and +3.9% over RTC in success; at Δ = 9 Jetson-PI keeps 92–97% success on the four suites vs VLASH 30–60% and RTC 81–93%.
- **Real robot:** X2-W robot with an XR-1 model on Orin (three 224×224 cameras, 15 Hz): picking 10/10, folding 8/10, placing 9/10, vs naive async on Orin 6/10, 0/10, 5/10.
- **Limitation (§7):** on-board compute and bandwidth remain far below GPU servers; gains may not scale with larger models.

## Relevance to SoftHier-VLA
Grounds the edge discussion in measured numbers: a 3B VLA is about 1.4 s per chunk on Orin at 50 W even after the model's own design tricks, and system-level graph optimization alone gives about 3× ([edge hardware and the 10 TOPS gap](../knowledge/edge-hardware-and-the-10-tops-gap.md)). Its action-expert time (536.8 ms of 1420.8 ms) shows the flow loop as a major cost on bandwidth-limited devices. See [serving methods](../knowledge/serving-methods.md).

See also: [vla.cpp](vla-cpp.md), [RTC](real-time-chunking.md), [FlashVLA](flashvla-streaming.md), [VLA-Perf](vla-perf.md), [XPU study](vla-xpu-characterization.md).
