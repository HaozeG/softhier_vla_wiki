---
type: paper
tags: [serving, workload-characterization, roofline, edge, energy, cost, npu, acceleration, recent]
sources: [arxiv:2604.24447, https://arxiv.org/abs/2604.24447v1]
---
# Characterizing Vision-Language-Action Models across XPUs: Constraints and Acceleration for On-Robot Deployment (Zhou et al.)

Zhou, Chen, Peng, Li, Li, Gu (Shanghai Jiao Tong University), arXiv 2604.24447 (v1, Apr 2026), ICML-format preprint. The leaderboard and profiling are the authors' measurements of public models; DP-Cache and V-AEFusion are the authors' own methods, evaluated by the authors. Leaderboard site: https://vla-leaderboard-01.vercel.app/.

## Summary
A deployment study of seven VLA and policy models (ACT, Diffusion Policy, SmolVLA, π0, π0.5, OpenVLA, GR00T) on seven platforms: an Intel CPU, NVIDIA RTX 4090, Jetson Thor and AGX Orin, Huawei Ascend 310B and 310P NPUs, and an Intel Arc B60 Pro. The paper has three parts:
- A leaderboard ranks model–platform pairs by cost, energy and time (CET), with latency and memory capacity as pass/fail gates. It concludes that smaller edge devices can beat a flagship GPU on cost or energy.
- Nsight Systems profiling and roofline points for π0 show a high-utilization, compute-bound VLM phase followed by a longer, low-utilization, memory-bound action-expert phase (RTX 4090 for the VLM; all three NVIDIA platforms for the action expert).
- Two training-free speedups, measured mostly on the RTX 4090:
  - DP-Cache reuses results across stable diffusion steps: 1.9× on Diffusion Policy, 1.29× on π0, and 6.0× on the 310P with ATC compilation.
  - V-AEFusion overlaps the VLM with the first denoising steps on the previous observation's features: 1.32× on the RTX 4090, 1.0–1.14× elsewhere.

Success rate is a single simulation score per model, assumed to be the same on every platform.

## Key claims
**Tiers and feasibility (§3.1, Fig 1, Table 10)**
- Models ("Consumers") split at 1B parameters: Small (ACT, Diffusion Policy, SmolVLA) and Big (GR00T, π0, π0.5, OpenVLA). Hardware ("Producers") split by peak FP16/BF16 throughput: Basic (Intel i7-11700 CPU, Ascend 310B), Standard (Intel B60 Pro, AGX Orin, Ascend 310P), Ultra (Jetson Thor, RTX 4090).
- Platforms (Table 10; BF16/FP16 peak, memory, bandwidth):

| Hardware      | BF16/FP16 TFLOP/s | Memory | Bandwidth  |
| ------------- | ----------------- | ------ | ---------- |
| Ascend 310B   | 10                | 12 GB  | 51.2 GB/s  |
| Ascend 310P   | 88                | 48 GB  | 204.8 GB/s |
| Intel B60 Pro | 90                | 24 GB  | 456 GB/s   |
| AGX Orin      | 42                | 64 GB  | 204 GB/s   |
| RTX 4090      | 330               | 24 GB  | 1000 GB/s  |
| Jetson Thor   | 258               | 128 GB | 273 GB/s   |

- Thor and B60 Pro have no official dense FP16/BF16 figure; the authors take half the INT8 TOPS (App A.1 footnote). All platforms run PyTorch through `torch.cuda`, `torch.xpu` or `torch.npu` (App A.1).
- Memory capacity is a hard gate next to latency: the 7B OpenVLA does not fit the 12 GB Ascend 310B; forcing big models onto the CPU via swap gives under 1 Hz. Basic Producers with Big Consumers are left out of the leaderboard (§3.1, §3.2).

**Leaderboard and CET (§3.2, Table 1, Fig 2–4)**
- CET = Cost, Energy, Time. Time (latency or control rate) is a pass/fail gate; cost (one accelerator per robot) and energy (battery) rank the pairs that pass. Score = mean LIBERO success over Spatial, Object, Goal, Long, treated as hardware-independent at the same precision. Energy is measured with a physical power meter.
- π0 rows (Table 1; score 86.0; cost / energy / time): RTX 4090 $3,500 / 2.398 kJ / 102.3 ms; Thor $3,400 / 1.282 kJ / 246.0 ms; Orin $1,999 / 1.866 kJ / 920.6 ms; B60 Pro $599 / 6.363 kJ / 306.5 ms; 310P $1,030 / 2.618 kJ / 818.0 ms.
- Finding #1: parameter count does not predict speed. Diffusion Policy (small) runs slower than π0 (big), which the paper attributes to 100 sequential denoising steps against π0's 4 (§3.2, Fig 2).
- Finding #2: the best platform depends on model and metric (Fig 4). Cost+energy ranking: Orin for SmolVLA, 310P for GR00T and π0. Cost+energy+time ranking: Thor for SmolVLA, 310P for GR00T, RTX 4090 for π0.
- Selection guideline for π0: latency priority → RTX 4090 (then Thor); cost priority → B60 Pro (then 310P); energy priority → Thor (then Orin) (§3.2).
- Real-robot energy (App A.2, Fig 12; π0.5 on a Franka arm, four-stage pick-and-place task, platforms that run at about 5 Hz). Inference hardware and arm power are measured separately. Total task time / inference-hardware energy: RTX 4090 55.50 s / 17.27 kJ; Jetson Thor 65.20 s / 8.71 kJ; B60 Pro 78.57 s / 34.58 kJ (read from the figure). The paper concludes that Thor is the most energy-efficient end to end and the RTX 4090 the fastest. No success rate is reported for this run.
- Fig 3 latency breakdown (vision, VLM, action expert, other) shows the action expert as the largest part of π0, SmolVLA and GR00T on every platform shown (read from the figure).

**Two-phase profile of π0 (§4.1, Fig 5; Nsight Systems on RTX 4090, AGX Orin, Jetson Thor)**
- Time share: vision 12%, VLM backbone 28% ± 1%, action expert 59% ± 1% (Fig 5).
- SM (streaming multiprocessor) utilization, vision / VLM / action expert: RTX 4090 45.6 / 89.8 / 21.8%; Orin 69.4 / 97.7 / 22.3%; Thor 77.1 / 94.9 / 38.6% (Fig 5).
- Finding #3: the VLM reaches about 3× the action expert's utilization, while the action expert takes about 2× the VLM's time. Because the action expert waits for the VLM, compute sits idle during the action-expert phase on Standard and Ultra platforms; this motivates V-AEFusion (§5.3).

**Roofline per phase (§4.2, Fig 6)**
- Framing: autoregressive LLM/VLM decoding is usually memory-bound (KV-cache reads) and video diffusion compute-bound (long sequences). Finding #4: VLA inverts this; the VLM backbone is compute-bound and the action expert memory-bound.
- VLM backbone: one forward pass, no autoregressive decoding. 18 decoder layers; each needs 185.1 GFLOPs and reads 110M parameters (220 MB), about 840 FLOP/byte, above the RTX 4090 ridge point of 330 FLOP/byte, so compute-bound on the RTX 4090.
- Action expert: small heads (300M for π0, 800M for GR00T) with 64.5 FLOP/byte on the RTX 4090. The paper says this intensity is the same on every platform and lies below the ridge points of Thor (945) and Orin (208), so the action expert is memory-bound on all three.
- Fig 6 places the action expert's decoder layer on all three platforms; the VLM's MLP and attention are placed on the RTX 4090 only.
- Stated implications: the VLM limits Basic and Standard platforms by compute; the action expert is limited by bandwidth, its serial denoising steps cannot be parallelized, and 10–100 steps make this worse on low-bandwidth platforms. The authors leave bandwidth-oriented optimization to future work (§4.2).

**Combining existing methods on OpenVLA (§5.1, Table 2)**
- Baseline OpenVLA needs 6 decode rounds per 7-DoF action. Applied: VLA-Cache (prefill), Spec-VLA (speculative decoding, decode phase), 4-bit quantization, each with its original default configuration.
- Speedup / mean LIBERO success: baseline 1.00× (5.41 Hz) / 76.5%; 4-bit 1.14× / 67.7%; cache 1.16× / 74.7%; speculative 1.11× / 75.1%; speculative + cache 1.29× (6.99 Hz) / 68.5%; 4-bit + cache 1.27× / 65.1%.
- Speculative decoding depends on the draft acceptance rate, which is sensitive to numerical precision, so quantization undermines it (§5.1).

**Compilation (§5.2.1, Table 3; π0, baseline → compiled)**
- `torch.compile` on NVIDIA; on Ascend the Ascend Tensor Compiler (ATC) compiles the whole workflow into a static graph for offline inference.
- RTX 4090 102.3 → 35.2 ms (2.90×, 28.41 Hz); Jetson Thor 246.0 → 163.0 ms (1.51×); Ascend 310P 818.0 → 350.0 ms (2.34×).

**DP-Cache (§5.2.2, Fig 7, Tables 4–6, Table 11)**
- Idea, borrowed from video-diffusion caching: the relative L1 change between consecutive diffusion steps, ‖x_curr − x_next‖₁ / ‖x_next‖₁, stays low over a middle "stable segment" for the model output, timestep embedding, noisy input, global feature and middle blocks. Inside that segment a computed result is reused for the following steps. The segment is fixed (about steps 20–80) by offline profiling before deployment (Fig 7).
- S = cache steps: S = 4 reuses a result for 3 steps and recomputes on the 4th.
- Diffusion Policy on RTX 4090 (Table 4; latency, Spatial / Object / Long success): baseline 378 ms, 75.4 / 52.4 / 74.1%; S = 4 200 ms (1.89×), 78.9 / 51.4 / 76.9%; S = 8 181 ms (2.09×), 71.6 / 46.1 / 73.4%. The text summarises S = 8 as 2.1× with a 3.6% success drop.
- π0 on RTX 4090, LIBERO (Table 11): 102 → 79 ms (1.29×), mean success 62.6 → 62.0%.
- π0.5-DROID on a Franka arm, table-cleaning task, 50 trials (Table 5): 95 → 74 ms (1.28×), success 76 → 70%.
- With compilation, Diffusion Policy (Table 6): RTX 4090 378 → 129 ms (2.9×, 7.7 Hz); Ascend 310P 1853 → 310 ms (6.0×, 3.2 Hz), where ATC alone gives 3.5× (1853 → 530 ms).
- Finding #5: optimizations for different phases (prefill vs decode) and different levers (compilation cuts per-step overhead, DP-Cache cuts iterations) must be composed, ideally in a unified framework like xDiT for image and video generation.

**V-AEFusion (§5.3, Fig 9–11, Tables 7–9)**
- Pipeline within one inference: while the VLM processes the current observation, the action expert starts its first denoising steps ("stale steps") on the previous observation's KV cache, then switches to the fresh KV cache for the remaining steps (Fig 9). This is distinct from overlapping inference with robot execution, which §2.2 lists as system-level pipelining (Real-Time Chunking, SmolVLA).
- Two stated justifications: (1) temporal coherence, measured: adjacent observations differ little (Fig 10), and layer-wise cosine similarity of the VLM's keys and values between adjacent inferences is 97.99% ± 0.8% and 96.91% ± 1.5% over 200 cycles; (2) coarse-to-fine generation, argued from the diffusion literature: early steps set the coarse trajectory and later steps on fresh features correct small deviations.
- Stale-step ablation (Table 7; fine-tuned π0 on a JAKA S5 dual-arm robot, 50 trials per task; block-in-bowl / cup-in-bowl success): 0 → 92 / 86%; 1 → 92 / 84%; 3 → 90 / 82%; 5 → 88 / 78%; 6 → 80 / 66%; 7 → 50 / 42%; 9 → 10 / 6%. The authors pick five stale steps, half of the action expert's steps, from the roughly 1:2 VLM-to-action-expert latency ratio (Fig 5).
- π0 on RTX 4090, LIBERO (Table 8): 102 → 77 ms (1.3×), mean success 62.6 → 62.3%; the text reports a 4% drop on the real-robot pick-and-place tasks.
- Across platforms (Table 9; baseline → V-AEFusion): RTX 4090 102 → 77 ms (1.32×); Orin 920 → 806 (1.14×); Thor 246 → 236 (1.04×); B60 Pro 306 → 292 (1.05×); 310P 818 → 820 (1.0×).
- DP-Cache skips a fixed set of steps, so its speedup is said to be consistent across hardware; V-AEFusion's depends on the platform (§5.3.2). Finding #6: the same method gains differently per platform; for V-AEFusion, on Standard devices (Orin, 310P) the VLM and action expert together exceed the hardware's capacity, so the overlap gains little.
- Both methods are training-free; the authors expect near-lossless results when combined with training-based methods such as consistency distillation (§5.3.1).

**Conclusion (§5.3.2, §6)**
- VLA inference has a "twofold serialization": the VLM-then-action-expert dependency (pipeline level) and the iterative denoising inside the action expert (component level). The authors expect the action expert to move from memory-bound to compute-bound as VLA models grow, and call for parallelism-centric designs combined with hardware-aware optimizations.
- Stated limitations: the leaderboard emphasises efficiency; the training-free optimizations may trade accuracy for latency; broader benchmarks, models and accelerators, dedicated action-expert optimizations and training-based methods are future work (§6).

## Caveats
- Table 1 energy is in kJ and Fig 3 in J (π0 on RTX 4090 about 2,400 J in both), but the paper does not say over what run or time window it is measured; it is not per inference (§3.2).
- The paper does not say what the Cost column includes (card, module, developer kit or full system) (§3.2).
- Peak FP16/BF16 figures are called dense (App A.1 footnote) but do not state accumulate precision; Thor and B60 Pro values are estimated from INT8 TOPS (App A.1).
- Test setup is mostly unstated. For the LIBERO score: no trial count, checkpoint, or whether the authors ran it. For latency: no input resolution, per-platform precision, warm-up or repeat count. Table 1 latency matches the uncompiled baselines of Table 3, so it is eager mode. Only the real-robot tables give trial counts (50 per task, Tables 5 and 7).
- Success rate is assumed, not measured, to be the same on every platform at equal precision (§3.2); each model gets one score.
- Control rate and success rate are not linked. The required control frequency is a user input to the feasibility filter (§3.2 guideline step ii); Fig 2 draws 1, 5, 10 and 30 Hz lines without assigning them to tasks. No experiment measures success rate as a function of platform latency. App A.2 runs three platforms on a real robot but reports only time and energy, without trial count or success rate.
- π0 has score 86.0 in Table 1 but 62.6 as the LIBERO baseline average in Tables 8 and 11.
- π0's denoising step count is inconsistent: Finding #1 says 4 steps, while §5.3.1 calls five stale steps half of the action expert's steps, which implies 10; §4.2 cites 10–100 steps for diffusion policies.
- The VLM is shown compute-bound on the RTX 4090 only. By the paper's own numbers its intensity (about 840) is below Thor's ridge point (945), yet Finding #4 is stated for VLA in general (§4.2, Fig 6).
- The bound classification rests on SM utilization from Nsight Systems and hand-computed intensity of one decoder layer per phase. The paper does not show how the action expert's 64.5 FLOP/byte is computed (token count, KV-cache reads) or how the Fig 6 points were measured.
- In Fig 6 the GemmaMLP and GemmaAttention points sit inside the box labelled "Action Expert", left of the ridge, while the caption calls them separately profiled VLM-backbone components and the text calls the VLM compute-bound. The figure does not resolve which module they belong to.
- The abstract's "up to 2.9× on GPUs" matches both compilation alone for π0 (Table 3) and DP-Cache plus compilation for Diffusion Policy (Table 6); "6× on edge NPUs" is DP-Cache plus ATC for Diffusion Policy on the 310P, of which ATC alone gives 3.5×.
- Table 2 (OpenVLA) and Table 5 (Franka) do not name the inference hardware. Table 4 tests Diffusion Policy, not a VLA, and omits the LIBERO Goal suite. Table 6 does not state S.
- The DP-Cache stable segment (steps 20–80) is defined for a 100-step diffusion; the paper does not say how it is applied to π0 or π0.5 with few flow steps (Tables 5 and 11).
- §5.1 motivates its choice by the VLM being compute-bound and aims at "reducing the arithmetic intensity per inference step", while §4.2 itself calls autoregressive decoding memory-bound, and OpenVLA's decode rounds are autoregressive.
- Thor, an Ultra-tier platform, gains only 1.04× from V-AEFusion (Table 9); Finding #6 names only Orin and 310P as capacity-limited and does not explain Thor. How the VLM and action expert run concurrently on one device (streams, scheduling) is not stated.
- §5.3.1 introduces V-AEFusion as reducing latency "beyond chunk fusion", a term the paper does not define.
- §3.2 says the selection guideline is validated on a Franka arm in App A.2, but A.2 reports only task time and energy for three platforms.

## Reading notes (inference)
Points the paper leaves unclear or argues weakly, from an in-depth reading. These are the readers' inferences, not claims of the source ([wiki-design decision 0015](../../wiki-design/decisions/0015-ingest-modes-brainstorm-or-in-depth.md)).
- **Cost compares unlike units (§3.2, Table 1).** The paper does not state form factors; the following is the readers' understanding, unchecked against vendor pages. Thor, Orin and the 310B are SoC boards with CPU, memory and storage on board, so they run alone. The RTX 4090, B60 Pro and 310P are add-in cards that need a host (CPU, memory, power supply, PCIe slot). If the Cost column is the accelerator alone, platform cost for the cards is understated, and the cost-priority pick (B60 Pro, $599) may not hold. The same question applies to energy: the paper does not say whether the power meter reading for a card includes its host.
- **"Success rate does not depend on the platform" is untested (§3.2).** Two reasons it may not hold. First, platforms run different kernels (ATC graphs on Ascend, `torch.xpu` on Intel), so even at the same nominal precision the numbers differ, and a denoising loop can accumulate the difference. Second, a LIBERO-style simulation waits for each inference, so latency cannot lower the score there; on a real robot a slower platform acts on older observations. The leaderboard therefore pairs a single simulation score with per-platform latency.
- **Low SM utilization does not by itself show a memory bound (§4.1–4.2).** Many small unfused kernels (elementwise, normalization) and launch gaps between them also leave SMs idle; the GPU is then limited by overhead, not by bandwidth. The paper's hand-computed intensity counts weight bytes only, so it does not change with fusion. Intensity measured from actual DRAM traffic would rise with fusion, as intermediate activations stop going through DRAM. The paper does not say whether the Fig 5 traces are compiled; if they are eager, note that compilation alone gives π0 2.9× on the RTX 4090 (Table 3), which suggests overhead is a large part of the uncompiled time. A per-kernel roofline (DRAM bytes measured per kernel) would separate the three cases.

## Related
See also: [Jung et al. workload characterization](vla-workload-characterization-kaist.md) (same two-phase split, RTX 4090 and Jetsons), [VLA-HWBench](vla-hwbench-edge-latency.md), [π0](../models/pi0.md), [π0.5](../models/pi05.md), [OpenVLA](../models/openvla.md), [SmolVLA](../models/smolvla.md), [GR00T N1](../models/gr00t-n1.md), [Diffusion Policy](../models/diffusion-policy.md).
