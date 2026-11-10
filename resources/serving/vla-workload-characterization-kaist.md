---
type: paper
tags: [serving, workload-characterization, roofline, dvfs, edge, jetson, closed-loop, recent]
sources: [arxiv:2610.05062, https://arxiv.org/abs/2610.05062v2, https://doi.org/10.1145/3845814.3850089]
---
# Beyond LLM Serving: Characterizing Vision-Language-Action Workloads for Embodied AI System Design (Jung et al.)

Jung, Moon, Jeong, Lee, Huh (KAIST), arXiv 2610.05062 (v2, Oct 2026); accepted at ASPLOS '27. Independent measurements of public checkpoints, not first-party claims about the models.

## Summary
A system-level characterization of VLA inference at batch size 1, the single-robot setting where each control period is a deadline. Four action-chunk models (GR00T N1.6, π0.5, OpenVLA-OFT, Cosmos-Policy) and an autoregressive OpenVLA baseline are profiled on an RTX 4090 edge server, Jetson Thor and Jetson AGX Orin. The paper uses stage-level latency, NCU roofline classification, DVFS sweeps and 43,200 closed-loop LIBERO episodes in MuJoCo. Main findings: the size of the tensors a stage processes decides whether it is memory- or compute-bound; platform balance shifts that bottleneck; GPU frequency scaling has a platform-dependent energy sweet spot; and overlapping inference with execution trades accuracy, speed and energy with no configuration best under every SLO.

## Key claims
**Setting and models (§1, §2, §3.1, Table 2)**
- **Framing (§1):** the ~33 ms control period is a recurring deadline, not a per-request latency target. Overruns leave the robot acting on stale observations and lower task success. Remote serving adds round-trip delay to the same budget, so execution is on-device or on a nearby edge server, at batch size 1.
- **Stated implications (§1 contributions; the authors' inference, not measured):**
  - `torch.compile` speedups differ by over 5× between action-head-dominated and backbone-dominated models. Compiler and kernel-level optimizations should therefore be applied selectively per architecture, targeting the stage that dominates: the action head in GR00T N1.6 and π0.5, the backbone in OpenVLA-OFT (also Takeaway 1, §4.1.2).
  - The memory/compute split "provides a basis for accelerator bandwidth-to-compute provisioning".
  - Runtimes should select operating points per SLO rather than use static configurations.
- Contact-rich manipulation needs a control period of about 33 ms (30 Hz). Measured inference takes 117–396 ms on the RTX 4090 (2.5–8.5 Hz effective) and 304–2603 ms on AGX Orin (0.4–3.3 Hz) (§2.2).
- LLM serving tools (continuous batching, paged KV cache, prefill-decode disaggregation) apply only partly: there is no request concurrency, the action-chunk models are not autoregressive, and the dominant stage varies with the architecture (§1, §6).
- Three action-chunk paradigms: iterative denoising over a compact `[B, action_horizon, action_dim]` tensor, run N times (typically 4–10); single-pass parallel decoding; unified video generation, where actions sit in slots of a video-diffusion latent (§2.1).
- Models (Table 2; config = denoising steps / about params / chunk length):

| Model         | Backbone                                      | Action head               | Config       |
| ------------- | --------------------------------------------- | ------------------------- | ------------ |
| GR00T N1.6    | Cosmos-Reason VLM (Eagle ViT + LLM)           | DiT, flow matching        | 4 / 3B / 16  |
| π0.5          | PaliGemma (SigLIP + Gemma 2B)                 | Gemma 300M, flow matching | 10 / 3B / 10 |
| OpenVLA-OFT   | Prismatic (SigLIP + DINOv2 + Llama 2)         | MLP, L1 regression        | N/A / 7B / 8 |
| Cosmos-Policy | Wan2.1 VAE (unified Cosmos-Predict2-2B model) | DiT, diffusion            | 5 / 2B / 16  |

- Cosmos-Policy has no separate action head. The VAE tokenizer encodes images into latent frames, and proprioception, the action chunk and future observations go into dedicated latent slots. A DiT denoises the target slots and actions are read from the action slots. The latent is 9 frames × 28×28 = 7,056 positions of 16 channels. For profiling, VAE = "backbone" and DiT = "action head" (§2.1).
- All runs use each repository's official LIBERO-finetuned checkpoint at its native resolution, precision and chunk length. Single-inference runs use random inputs of the right shapes (§3.3, §4).

**Autoregressive baseline (§2.1, Table 1; OpenVLA, RTX 4090, eager, 7-D action)**
- Vision encoder 16.03 ms (76.1% of its GPU time compute-bound); LLM prefill 43.50 ms (86.4% compute-bound); 6 cached-decode passes 140.90 ms (100% memory-bound); other 9.13 ms; E2E 209.56 ms. Decode is 67% of E2E and 3.2× prefill.
- The KV cache grows by only D − 1 positions and is discarded after each action, so there is little to reuse. OpenVLA-OFT's reported LIBERO action throughput is about 26× this baseline's.

**Stage latency (§4.1, Fig 3–4; RTX 4090, eager)**
- E2E and split (backbone or VAE / action head or DiT): GR00T N1.6 120 ms (42 / 78, head 65%); π0.5 294 ms (73 / 221, 75%); OpenVLA-OFT 117 ms (backbone 117, 99%; MLP head 0.6 ms); Cosmos-Policy 396 ms (114 / 282, 71%).
- Per-stage `torch.compile` speedup: π0.5 head 7.96×, GR00T N1.6 head 4.42×, OpenVLA-OFT backbone 1.42×, Cosmos-Policy DiT 0.97× (TransformerEngine-based, slower when compiled). Takeaway 1: the architecture decides the dominant stage and where compilation helps.

**Roofline (§4.2, Fig 5–7; RTX 4090: 165.2 TFLOP/s FP16, 1.008 TB/s, ridge 163.9 FLOP/B)**
- GPU time memory-bound: GR00T N1.6 62%, π0.5 58%, concentrated in the action heads. Compute-bound: OpenVLA-OFT 84%, Cosmos-Policy 77%.
- Share of GPU time by stage and bound (Fig 5, read from the figure; compute-bound / memory-bound):
  - GR00T N1.6: ViT 17.0, prefill 12.4, head 8.2 / prefill 8.3, head 50.2.
  - π0.5: ViT 10.0, prefill 30.0 / prefill 8.5, head 46.1.
  - OpenVLA-OFT: ViT 13.0, prefill 70.9 / prefill 11.5.
  - Cosmos-Policy: VAE 15.7, DiT 61.2 / VAE 10.5, DiT 12.5.
- The text says GEMMs dominate GPU time in every model and stage (§4.2). Operator shares in Fig 6 (read from the figure):
  - Action heads: GR00T N1.6 GEMM 69%, elementwise/activation 19%; π0.5 GEMM 48%, elementwise/activation 44%; OpenVLA-OFT head GEMM 81%.
  - Cosmos-Policy: DiT GEMM 72%; VAE convolution 64%, elementwise 33%.
- GR00T N1.6 and π0.5 action-head GEMMs sit below the ridge point. At batch 1 their linear layers reuse weights across only a few action and state tokens, and the denoising loop repeats them each step. OpenVLA-OFT backbone and Cosmos-Policy DiT GEMMs sit above it (Fig 7). Takeaway 2: tensor dimensionality sets the bound.

**Edge SoC sensitivity (§4.3.1, Fig 8; compiled)**
- Sensitivity S = latency with one clock domain at minimum ÷ latency with all at maximum; R = S_GPU / S_EMC (EMC = external memory controller, sets DRAM bandwidth). R < 1 means more bandwidth-sensitive.
- Orin: memory-bound heads R = 0.81 (GR00T N1.6), 0.83 (π0.5); compute-bound stages 1.03–1.67.
- Thor: every stage R < 1. GPU throttling over 3.6× gives 1.3–2.3× slowdown, EMC throttling 3.3–4.7×. GR00T N1.6 head 0.30, π0.5 head 0.33, GR00T N1.6 backbone 0.44, Cosmos-Policy VAE 0.50, DiT 0.59. The OpenVLA-OFT backbone (0.27) breaks the ordering. Takeaway 3: the bound depends on both intensity and the platform's compute-to-bandwidth ratio.

**Energy under DVFS (§4.3.2–4.3.4, Fig 9–10, Table 6)**
- GPU-clock sweep: on Orin all four models reach minimum energy at 510 MHz, saving 24–32% at 1.9–2.2× latency. On Thor the savings are only 1–4%. EMC throttling raises energy on both SoCs (+32 to +60% Orin, +56 to +110% Thor). Takeaway 4.
- Phase-aware policy (CPU and EMC at maximum, one GPU clock per phase, 25 combinations), with clock-switch time excluded. GR00T N1.6: Orin −18.1% latency / −2.4% energy; Thor −18.8% / −7.5%. π0.5: Orin −2.0% / −17.9%; Thor −18.4% / −6.0%. Cosmos-Policy has no gain (phases too alike). OpenVLA-OFT's 0.6 ms head is shorter than one transition.
- Clock-switch cost: 3.5 ms per transition on Orin, 8.6 ms on Thor. Two switches cost 13.6% of GR00T N1.6's E2E on Thor, which eats most of its gain. Takeaway 5.

**Closed loop (§5, Table 7, Fig 11–14)**
- Setup: a MuJoCo client pulls actions from a FIFO queue every Δt. The next inference starts when ⌈K·p⌉ steps remain (overlap percentage p ∈ {10, 25, 50}%). Δt = 1.5 × RTT_max / ⌈K·p⌉, so the control period is set per configuration, not fixed at 33 ms. The observation (about 384 KB) and the chunk (about 0.5 KB) travel over WebSocket. Scale: 4 models × 3 platforms × 3 overlaps × 40 tasks × 30 rollouts = 43,200 episodes. LIBERO-10 = "Long" group; Goal + Spatial + Object = "Short" group.
- RTT_max (synchronous, compiled, including transfer), RTX 4090 / Thor / Orin: GR00T N1.6 142.8 / 126.7 / 206.8 ms; π0.5 136.1 / 180.6 / 457.3; OpenVLA-OFT 148.7 / 306.8 / 528.2; Cosmos-Policy 442.9 / 1023.0 / 2558.4 (Table 7).
- Raising p from 10% to 50% lowers success rate, shortens episodes and raises energy. Accuracy loss depends on the model: π0.5 loses least, then OpenVLA-OFT, then GR00T N1.6 and Cosmos-Policy (RTX 4090: 15–20 pp vs 31–49 pp). Speedup is about the same on every platform (Long group: GR00T N1.6 2.8–3.0×, π0.5 3.6–3.9×). Energy growth depends on the platform (Cosmos-Policy RTX 4090 up to 5.1×, GR00T N1.6 1.9–2.1×, edge SoCs 1.5–2.9×). Takeaway 6.
- Efficiency ("tokens/s" = generated actions per second): RTX 4090 GR00T N1.6 about 59 actions/s at 186 J per successful episode vs Cosmos-Policy about 17 at 2,632 J; Thor GR00T N1.6 58 at 73 J vs Cosmos-Policy over 1,000 J. Models dominated by memory-bound heads are over 10× more efficient per joule. Takeaway 7.
- SLO picks (budget = p25 of measured configurations, highest-SR feasible point): π0.5 wins all four. Time 15.6 s → RTX 4090, Long 50% (82.7%), Short 25% (96.1%). Control cycle 75.2 ms → RTX 4090 25% (93.0%, 96.1%). Edge power 2.1 W and energy 98.0 J → Thor 10% (95.7%, 99.1%; 93.5 J and 44.4 J). Minimum energy at SR ≥ 85% → GR00T N1.6 on Thor 10% (Long 86.3% at 34.8 J, Short 93.9% at 16.8 J). Takeaway 8: no Pareto-dominant configuration.

**Discussion (§6, the paper's own suggestions; no accelerator is proposed)**
- A runtime interface should expose per-stage cost, chunk progress, observation freshness and SLOs, so a scheduler can choose timing, overlap, resources and where each stage runs.
- Hardware features the authors expect to help:
  - high tensor throughput for backbone and video-DiT GEMMs;
  - high utilization on many small fixed-shape GEMMs in denoising loops;
  - more bandwidth for memory-bound heads;
  - low kernel-launch and control overhead;
  - on-chip storage that keeps the head's weights across denoising steps, which are reloaded every step;
  - faster clock transitions.
- Kernel fusion, graph capture, step distillation, feature caching and weight-only quantization still apply at batch 1. Continuous batching, paged KV and speculative decoding mostly do not. Only compilation was measured; the rest is argued from workload structure.

## Caveats
- Simulation only (MuJoCo, LIBERO). No real robot, sensor pipeline, network jitter or contact effects. All hardware is NVIDIA. 1-step distilled heads are excluded (§6).
- Energy covers only the GPU (RTX 4090) or the compute rails (SoCs). Compare within a platform; cross-platform figures show only trends (§3.3, §6).
- Modes differ by analysis. Stage latency and roofline use eager mode. DVFS and closed loop use the compiled settings of Table 5 (GR00T N1.6 backbone default mode; Cosmos-Policy all eager). Table 7 RTT includes transfer and pre/post-processing.
- §6 quotes compile speedups of "4.4–7.4×" for iterative heads, while §4.1.2 reports 4.42× and 7.96×. Table 6 gives 18.0 ms per inference on Thor, more than 2 × 8.6 ms. Both are as printed.
- The paper does not give the slot layout of Cosmos-Policy's 9 latent frames, how actions are encoded into a latent frame, or how language enters. Those are in Cosmos-Policy's own paper (ref [22]).
- Fig 6 does not fully support "GEMMs dominate GPU time in every model and stage" (§4.2). Cosmos-Policy's VAE is mostly convolution (64%), and π0.5's action head is 48% GEMM against 44% elementwise.
- Fig 7 draws three ridge lines, one per precision (FP16->FP16 dense, BF16->FP32 dense, FP32 CUDA). The text gives one ridge point, 163.9 FLOP/B from 165.2 TFLOP/s FP16, without saying which line it is. The numbers in the Fig 7 legend (for example GR00T N1.6 action head 1464, OpenVLA-OFT action head 5) are unlabelled; they look like GEMM kernel counts.
- Roofline attribution is done on the RTX 4090 only. The Jetsons share DRAM and expose only aggregate bandwidth (§3.2).

## Reading notes (inference)
Points the paper leaves unclear or argues weakly, from an in-depth reading. These are the readers' inferences, not claims of the source ([wiki-design decision 0015](../../wiki-design/decisions/0015-ingest-modes-brainstorm-or-in-depth.md)).
- **M3 (§2.3) is argued weakly.** The stated reason, that platforms differ in compute, bandwidth and power so one tier does not transfer, holds for any set of platforms, including datacenter accelerators from different vendors. The platform-dependent bottleneck shift shown in §4.3 is the general roofline principle (a kernel's bound depends on its arithmetic intensity relative to the platform's ridge point), not something specific to the edge. What the paper shows that is specific to its edge setting: unified CPU-GPU memory with only aggregate bandwidth (§3.2), power caps, per-inference energy under DVFS, and clock-transition cost (§4.3).
- **Why the iterative heads gain most from compilation is only hinted at.** The paper attributes it to repeated dispatch of small kernels (§4.3.3 rule i, §6). Fig 6 shows π0.5's head spends 44% of GPU time in elementwise and activation kernels, against 19% for GR00T N1.6's head. Fusing such kernels into their neighbours, and removing launch overhead with CUDA graphs, is a plausible cause of its 7.96× gain against 4.42×, but the paper does not break the speedup down.
- **The Thor energy explanation does not follow (§4.3.2).** The paper explains Thor's small GPU-throttling saving (1–4%) by GPU throttling having "limited impact on latency across all stages". If latency barely changes while GPU clock drops, energy would be expected to fall more, not less. The stated reason does not explain the result, and the paper gives no other (for example, the GPU's share of the measured rail power).
- **Simulation time is not specified (§2.2, §5.1, §6).** The paper does not say whether simulated time advances with the wall clock between actions, and links no code. Standard LIBERO steps robosuite with an `OSC_POSE` controller at `control_freq=20` (LIBERO repository, `envs/env_wrapper.py`): each action is an end-effector pose delta applied for a fixed simulation step. If the authors kept this, every model gets the same ⌈K·p⌉ stale steps whatever its latency. The success comparison then measures robustness to a fixed staleness, not real-time task success, and slowness shows only in wall-clock time and energy. If the simulation follows the wall clock, slower models also lose success to their latency, and the comparison holds as deployment evidence. On a real robot, each action would last Δt of real time, so a slow configuration would be staler and would run actions at a different rate than in training. The paper's own validity claim is limited to "controlled conditions" (§6), and its listed limitations do not mention this choice. Takeaways 6 and 8 and the SLO picks of Fig 14 combine success rate with episode time as if it were deployment evidence.
- **The platform-invariant speedup follows from Eq 5 (§5.2).** Δt is set proportional to RTT_max / ⌈K·p⌉, so from p = 10% to 50% the control period shrinks by a ratio that depends only on ⌈K·p⌉: 8/2 = 4× for K = 16, 5/1 = 5× for K = 10. The measured episode-time reductions (2.8–3.0× for GR00T N1.6, 3.6–3.9× for π0.5) fall below these ratios, and their stability across platforms follows mostly from this construction. The paper attributes it to stage-proportion stability instead, and mentions the calibration only as a second reason.
- **Fig 2 and §5.1 describe different queue behaviour (§2.2, §5.1).** Fig 2 draws each new chunk from the time its observation was captured and shades its first actions, whose time slots passed during inference, which implies those stale actions are skipped. The legend's "already executed actions" means slots already executed by the previous chunk. §5.1 and Fig 11 describe a FIFO queue that consumes a_0, a_1, ..., which implies a new chunk runs from its first action. The paper does not say which one the closed-loop runs use, and the two give different staleness.
- **Takeaway 7 is a correlation across four models (§5.3).** The paper's wording is careful ("corresponds to", "consistent with"), but it places the result next to the roofline analysis. Other differences among the four models could explain the energy gap: total work per action (Cosmos-Policy's DiT processes 7,056 positions per step), and wall-clock episode length. Under Eq 5 a slower model gets a longer Δt, so static power accrues over a longer episode even while the GPU idles. No experiment varies the bound of one model's head while holding the rest fixed.
- **Overlap and control rate are coupled (§5.1, Fig 12).** Eq 5 shrinks Δt as p grows, so the same latency spans more control steps (about ⌈K·p⌉/1.5), and the success drop with p mixes earlier triggering with a faster control rate. Real deployments use either regime:
  - **Fixed control rate** (π0 runs its robots at a fixed 20 or 50 Hz): the same latency spans the same number of steps, and p mainly sets feasibility. Inference must finish within ⌈K·p⌉ steps, so latency sets a minimum overlap, and a slow configuration may not keep up at any p. A policy that replaces the old chunk's unexecuted actions would re-plan more often as p grows at the same staleness, which would be expected to raise success rather than lower it.
  - **Rate set by model speed** (RT-2 at 1–3 Hz, OpenVLA at about 6 Hz): Eq 5 matches this regime in form. On a real robot each action then lasts longer in real time and the world keeps moving during inference, a cost the paper's simulation may not reproduce (see the simulation-time note above).

  The paper's sweep answers how success changes when overlap and control rate change together. Which queue policy was used is open (Fig 2 vs §5.1).
- **The batch-size link is not stated.** In datacenter serving, batch size is a knob: raising it raises arithmetic intensity and can move a memory-bound stage toward the ridge point of whatever hardware is used. A single robot fixes the batch at 1, which fixes each stage's intensity, so platform balance alone decides the bound. The paper relies on batch 1 throughout but does not draw this connection.
- **"Higher p increases observation staleness" (§5.1) is ambiguous under Eq 5.** Eq 5 holds ⌈K·p⌉ × Δt at 1.5 × RTT_max, so the time from capture to the start of the new chunk is the same for every p. What grows with p is the number of actions executed on the old observation (⌈K·p⌉, with a shorter Δt). The paper does not say which of the two it means.

## Related
See also: [Zhou et al. (SJTU)](vla-xpu-characterization-sjtu.md) (π0 two-phase profile, Ascend and Intel platforms, cost and energy), [RT-2](../models/rt-2.md) and [OpenVLA](../models/openvla.md) (token-based), [π0](../models/pi0.md) (flow-matching family), [OpenVLA-OFT](../models/openvla-oft.md), [π0.5](../models/pi05.md), [GR00T N1](../models/gr00t-n1.md) (the earlier version), [SmolVLA](../models/smolvla.md) (asynchronous inference), [WAM survey](../surveys/survey-world-action-models-nus.md) (lists CosmosPolicy).
