---
type: paper
tags: [serving, workload-characterization, benchmark, roofline, edge, jetson, amd, quantization, recent]
sources: [arxiv:2610.34717, https://arxiv.org/abs/2610.34717]
---
# VLA-HWBench: Where the Time Goes When VLA Models Run on Edge Hardware (Xu et al.)

Xu, Tan, Jiang, He (National University of Singapore), Wu, Zeng, Heinrich (0G Labs), arXiv 2610.34717 (Oct 2026). Independent measurements of public checkpoints, not first-party claims about the models.

## Summary
A latency benchmark of 18 open VLA models (19 configurations) at batch size 1 on two edge platforms with CPU–GPU shared memory: NVIDIA Jetson AGX Thor and AMD Ryzen AI Max+ PRO 395. Each call is split into seven stages, from CPU preprocessing to postprocessing. The paper asks three questions: where the time goes, how much optimizations help, and what limits the remaining time. Its answers: latency spans up to 157× and follows the number and cost of action-generation iterations rather than parameter count; kernel fusion with low-bit weights (FlashRT on the Jetson, for π0.5 and GR00T N1.7 only) gives the largest gain and moves time to stages it shortens least, such as CPU preprocessing; after optimization, memory bandwidth limits the few-token denoising steps on the Jetson while software limits vision encoding, prefill and preprocessing. It measures latency only, open loop on one observation, and no task success.

## Key claims
Notation: the paper writes **T** for the latency of one call and **N** for the number of action-generation iterations; both differ from the wiki's symbol conventions. Its **S0–S6** are stages of one model call (S0 = CPU preprocessing), not the System 0/1/2 layers of a robot stack.

Scope: the timed span ends at the host-side action chunk (§3.1), and every configuration runs open loop on one fixed LIBERO-10 observation (§4.4). No simulator step and no low-level controller that executes the actions are timed or run.

**Motivation and gaps (§1, §2, Table 1)**
- Edge inference is motivated by stale observations in closed-loop control, variable wireless links and privacy of camera data (§1).
- Three gaps in prior measured studies (Taherin et al., Zhou et al., Vishwanathan et al.) and the analytical VLA-Perf (§1):
  - They cover at most five models and two of the four action-generation forms (flow matching, parallel decoding, token-by-token, reasoning then acting).
  - They split a call into at most three phases, and none times CPU preprocessing.
  - None evaluates a specialized backend, and only one tests low-bit weights. Each backend (TensorRT, FlashRT, Embodied.cpp, vla.cpp) is evaluated only on the models it targets.
- Comparison with prior studies (Table 1; "Forms" = action-generation forms covered, "Stages" = phases a call is split into):

| Study               | Models | Forms | Measured | Non-NVIDIA edge | Stages | CPU prep. | Backend | Low-bit | Real input |
| ------------------- | ------ | ----- | -------- | --------------- | ------ | --------- | ------- | ------- | ---------- |
| Taherin et al.      | 5      | 2     | yes      | no              | –      | no        | no      | no      | no         |
| Zhou et al.         | 5      | 2     | yes      | yes             | 3      | no        | no      | yes     | no         |
| Vishwanathan et al. | 1      | 1     | yes      | no              | 3      | no        | no      | no      | no         |
| VLA-Perf            | –      | 3     | no       | no              | 3      | no        | no      | no      | no         |
| VLA-HWBench         | 18     | 4     | yes      | yes             | 7      | yes       | yes     | yes     | yes        |

**Setup in brief (§1)**
- 18 open VLA models covering all four forms, chosen by Hugging Face downloads and GitHub stars. Each runs in a reference configuration (eager PyTorch, optional optimizations off) on the same LIBERO-10 observation and timing boundary.
- Compilation, specialized backends (TensorRT, FlashRT) and lower precision are enabled one at a time on two models, π0.5 and GR00T N1.7, and each gain is attributed to stages.

**Headline answers (§1, Fig. 1)**
- Q1: without optimizations, action generation is the largest stage in 14 of 19 configurations on the Jetson. Latency spans 77 ms to 6.3 s on the Jetson (82×) and 114 ms to 17.9 s on the AMD platform (157×). Only 10 (Jetson) and 9 (AMD) of 19 configurations generate actions as fast as LIBERO executes them.
- Q1, Fig. 1: a least-squares fit of log latency on log parameter count explains at most 15% of the variance; latency follows the number of action-generation iterations instead. In the figure, the autoregressive and reasoning configurations sit at the top on both platforms, at parameter counts similar to the fast flow-matching ones.
- Q2: on the Jetson, compilation, a specialized backend and lower precision speed up π0.5 by 2.5×, 1.8× and 1.6× in turn (7.2× total) and GR00T N1.7 by 1.02×, 1.4× and 1.8× (2.6× total). Kernel fusion with 4-bit weights gives the largest gain, 2.6–2.9× over compilation, but exists only for these two models and only on the Jetson. CPU preprocessing grows from 12% to 39% of the GR00T N1.7 call.
- Q3: no single resource limits the optimized call. Action generation and other few-token stages are memory-bound and on the Jetson run above half the peak memory bandwidth. Vision encoding and long prefills reach 6–42% of the hardware bound (unfused kernels, missing low-precision support). CPU preprocessing is limited by serial Python and idle-thread wake-ups.
- Stated implications (authors' recommendations, §1 and abstract): edge VLAs should reduce action-generation iterations (fewer denoising steps or parallel decoding) rather than shrink the model; inference software should extend kernel fusion and low-bit execution to more models and platforms and optimize host preprocessing; edge hardware should prioritize memory bandwidth and a fast host CPU over peak GPU compute.

**Latency model and metrics (§3, Fig. 2, Appendix Table 6)**
- A call maps camera images, proprioceptive state and an instruction to a chunk of H actions. Latency T runs from the host-side observation to the host-side action chunk and splits into seven stages, T = Σ T_k (Eq. 1):

| Stage                | Work                                      | Unit        | Measured by                       |
| -------------------- | ----------------------------------------- | ----------- | --------------------------------- |
| S0 Preprocessing     | resize, normalize, tokenize               | CPU         | timer                             |
| S1 Host-to-device    | copy the inputs                           | copy engine | timer                             |
| S2 Vision encoding   | images to tokens                          | GPU         | timer or kernel trace             |
| S3 Prefill           | language model, fills the key–value cache | GPU         | timer or kernel trace             |
| S4 Action generation | denoising steps or decoded tokens         | GPU         | timer, step sweep or kernel trace |
| S5 Postprocessing    | unnormalize, copy back                    | CPU         | timer                             |
| S6 Residual          | T minus S0–S5 (e.g. Python dispatch)      | CPU         | derived                           |

- Action generation runs N iterations in sequence, T₄ ≈ N·t, with t the cost of one iteration (Eq. 2). N is the number of denoising steps (flow matching), one (parallel decoding), the number of generated tokens (autoregressive), or reasoning tokens plus action iterations (reasoning models).
- Fig. 2 draws the chunk as H actions of which the first H_e are executed.
- Metrics per question (§3.2):
  - Q1: stage shares T_k/T, latency T and time per action T/H in the reference configurations. LIBERO's controller runs at 20 Hz (one action per 50 ms), and a model "keeps up" only if T/H < 50 ms.
  - Q2: speed-up T₀/T over the reference latency T₀, plus agreement of the actions before and after each compilation and precision step.
  - Q3: roofline. A GPU stage with F floating-point operations and W bytes **of weights** takes at least max(F/P, W/B), with P the peak matrix-unit throughput in its number format and B the peak memory bandwidth. It is memory-bound if F/W is below the ridge point P/B. A stage close to its bound is limited by hardware, one far from it by software.
- Design principles (§3.3): run each model through its own LIBERO evaluation entry point with the authors' pinned library versions; add optimizations one at a time on fixed weights and input; synchronize the device at every stage boundary and check that stages add up to T; split CUDA-graph-captured stages by their kernels. The two platforms differ by 4.4× in peak 16-bit throughput but only 1.1× in memory bandwidth, which the paper uses to separate host, GPU and memory effects.

**Models, backends, platforms and protocol (§4, Tables 2–4)**
- Models: 18 open VLAs released in 2025–2026 with strong LIBERO success, a public LIBERO checkpoint with evaluation code and wide use (Table 5: GitHub stars, Hugging Face downloads). MolmoAct2's two action heads give 19 reference configurations, each run with its LIBERO-10 checkpoint and its own evaluation settings (§4.1).

| Action generation     | Model (params B, weights, H)                                                                                                                                                                                                                                                                            |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Flow matching         | X-VLA (0.88, BF16, 30), GR00T N1.7 (3.14, BF16, 16), SmolVLA (0.45, BF16+FP32, 50), InstructVLA (2.60, BF16+FP32, 8), π0.5 (4.14, BF16+FP32, 50), NORA-1.5 (3.99, BF16, 5), Evo-1 (0.78, BF16+FP32, 50), FastWAM (6.02, BF16, 32), MolmoAct2 flow (5.44, BF16, 10), InternVLA-A1.5 (2.68, BF16+FP32, 8) |
| Parallel decoding     | VLA-Adapter (1.47, BF16, 8), SimpleVLA-RL (7.54, BF16, 8), OpenVLA-OFT (7.71, BF16, 8), RIPT-VLA (7.99, BF16+FP32, 8)                                                                                                                                                                                   |
| Autoregressive tokens | pi0-FAST (3.45, BF16+FP32, 10), MolmoAct2 discrete (5.44, BF16, 10), VLA-0 (3.75, BF16, 8)                                                                                                                                                                                                              |
| Reasoning, then act   | DeepThinkVLA CoT (2.92, BF16, 10), MolmoAct2-Think cold (5.45, BF16, 10)                                                                                                                                                                                                                                |

- Backends (§4.2): LeRobot 0.6.1 (PyTorch, optional torch.compile), the authors' own LIBERO entry point, FlashRT (fused kernels in captured CUDA graphs, FP8 and NVFP4 weights) and TensorRT. FlashRT and TensorRT run only on the Jetson. Q1 uses LeRobot or the authors' code with every optional optimization off; Q2 adds optimizations only to π0.5 and GR00T N1.7.
- The reference configuration switches off defaults some checkpoints ship with: LeRobot's compile option for π0.5 and pi0-FAST, CUDA graphs for MolmoAct2 (Appendix A.1).
- Execution horizon H_e equals H except GR00T N1.7 (16, 8) and VLA-0 (8, 1); views per call are 2 except NORA-1.5 and SimpleVLA-RL (1) and SmolVLA (3) (Table 4).
- Platforms (Table 3), both with CPU and GPU sharing 128 GB LPDDR5X:

|                     | Jetson AGX Thor (T5000)         | Ryzen AI Max+ PRO 395                         |
| ------------------- | ------------------------------- | --------------------------------------------- |
| GPU                 | Blackwell, 2560 CUDA cores      | RDNA 3.5, 40 CUs                              |
| CPU                 | 14 Neoverse-V3AE cores, 2.6 GHz | 16 Zen 5 cores, 5.1 GHz                       |
| Memory bandwidth    | 273 GB/s                        | 256 GB/s                                      |
| FP16 / FP32 TFLOP/s | 258 / 8.1                       | 59.4 / 29.7 (derived from CU count and clock) |
| FP8 / FP4 TFLOP/s   | 517 / 1035                      | –                                             |
| Power               | 40–130 W                        | 45–120 W                                      |
| Software            | CUDA 13.2, PyTorch 2.11         | ROCm 7.2, PyTorch 2.14                        |

- Protocol (§4.4): one real LIBERO-10 observation (two 256×256 images, robot state, instruction), adapted only where a release's input contract requires. Each configuration runs in its own process: 20 warm-up calls, then up to 100 timed calls (trimmed to fit 90 s, at least 20), each bracketed by device synchronization; the median is reported. A second run over 24 frames of one episode checks how input content changes latency.
- Stage attribution (§4.4): reference configurations run without CUDA graphs, so each stage boundary in a release's code is timed directly; a stage run inside another is counted in that one. The cost of one denoising step or camera view is the slope b of a fit T = a + bN. CUDA graphs of optimized configurations are split into stages by kernel order and repetition.
- Profiling (§4.4): PyTorch's profiler sorts kernels into matrix-unit GEMM or attention, GEMMs without matrix units, and others; operator shapes and formats from an eager run give F and W per stage. CPU preprocessing is studied by timing sub-steps, varying thread count and reading core idle-state counters.

**Q1: where the time goes (§5.1, Figs. 3–4, Appendix Tables 7–8, 10–11)**
- Action generation is the largest stage in 14 of 19 configurations on the Jetson, at 42–99% of the call. The five exceptions (the four parallel decoders and Evo-1) spend more in prefill or vision encoding; so does π0.5 on the AMD platform, whose FP32 vision tower encodes three image slots, one empty. A stage that the software fuses into another is counted in that one (e.g. SimpleVLA-RL's action generation inside prefill, Table 8).
- Latency spans 77 ms (X-VLA) to 6.3 s (VLA-0) on the Jetson and 114 ms to 17.9 s on the AMD platform, with a similar ranking (Spearman ρ = 0.91). Only 10 (Jetson) and 9 (AMD) of 19 configurations keep T/H under 50 ms.
- Long chunks hide slow calls: π0.5 spends less time per action than VLA-Adapter though its call takes 4.4× longer (Fig. 4b).
- Model size: the log-log fit of latency on parameter count explains 9% of the variance on the Jetson and 15% on the AMD platform. GR00T N1.7 (3.1 B) and VLA-0 (3.8 B) differ by 53× on the Jetson; OpenVLA-OFT has 5.2× VLA-Adapter's parameters but is only 2.7× slower.
- Iterations (Eq. 2): on the Jetson one flow-matching step costs 4–107 ms and parallel decoding needs one iteration, while autoregressive heads pay one language-model pass of 20–52 ms per token. VLA-0's 208 decimal tokens take 99% of its call; the reasoning tokens of DeepThinkVLA and MolmoAct2-Think about 91%. On identical weights, MolmoAct2's discrete head is 2.3× slower than its flow head.
- Input dependence: the four configurations with scene-dependent token counts vary by 12–122% across 24 frames (Table 11; MolmoAct2 discrete 122%, pi0-FAST 38–42%).
- Per-step cost b from T = a + bN (Table 10, Jetson): 3.9 ms (Evo-1) and 4.9 ms (X-VLA) up to 106.8 ms (InternVLA-A1.5); π0.5 14.7 ms, GR00T N1.7 15.7 ms.
- Insight 1 (authors): latency follows the number of action-generation iterations, not parameter count; token-by-token decoding and reasoning cannot keep up with 20 Hz while flow matching over long chunks can; future edge VLAs should cut iterations (fewer denoising steps, parallel decoding or longer action chunks) rather than shrink the model.

**Q2: optimizations and where the time moves (§5.2, Fig. 5, Appendix F, Tables 12–14)**
- Three levels, least to most invasive, on π0.5 and GR00T N1.7 (the two models for which all exist): automatic (compile the unchanged model), specialized backend (FlashRT for both, TensorRT for GR00T N1.7), lower precision (FP8 or NVFP4 weights inside FlashRT). All π0.5 rows use FlashRT's workload (10 actions, two image slots), whose eager reference is 318 ms rather than Q1's 405 ms.
- Compilation helps only when it captures the whole model. LeRobot's option captures the whole π0.5 call in one CUDA graph (kernel launches 13k → 15) and also switches FP32 matrix multiplications to TF32: 2.5× on the Jetson, 1.8× on the AMD platform (no TF32). Isaac-GR00T's recipe compiles only the action head: that stage gains 1.4× but the uncompiled vision encoding and prefill slow down, so the call gains 1.02× on the Jetson.
- Backend: FlashRT is 1.8× (π0.5) and 1.4× (GR00T N1.7) faster than the level before; TensorRT gains less for GR00T N1.7 (1.24× over PyTorch) because it keeps the vision encoder in FP32. FlashRT also runs π0.5's FP32 layers in FP16.
- Precision: FP8 and NVFP4 add 1.3–1.8×, mostly in action generation (Table 12: π0.5 72.8 → 47.9 ms FP8, → 44.4 ms NVFP4; GR00T N1.7 80.7 → 60.9 ms FP8, → 45.6 ms NVFP4). In total π0.5 falls from 318 to 44 ms on the Jetson (7.2×) and GR00T N1.7 from 119 to 46 ms (2.6×). In π0.5's NVFP4 configuration only the language model's FFN uses NVFP4; the vision tower and action expert use FP8. GR00T N1.7 runs every GEMM of its action head in NVFP4 (Appendix G).
- Action agreement (Table 14, 11 frames): FP8 keeps cosine similarity to FP16 actions at 0.998 or higher, NVFP4 at 0.93 or higher; π0.5 NVFP4 max |Δ| is 0.677 against 0.096 between repeated calls. FP8 scales are calibrated once at load time on the benchmark observation, which is also the first of the 11 frames (Appendix F).
- Compiled π0.5 actions differ by up to 2.0, a flipped gripper command, between two compiled processes on the Jetson and from eager on the AMD platform, against 0.07 between repeated calls in one process; repeated SmolVLA calls already differ by up to 1.96 (Appendix F).
- Time moves to the stages optimization shortens least (Fig. 5c,d): π0.5 vision encoding falls from 33% to 13% of the call while prefill rises from 14% to 34%; GR00T N1.7's CPU preprocessing, untouched by any optimization, grows from 12% to 39%.
- AMD: only compilation exists, so optimization widens the Jetson lead from 2.0–2.5× to 5.7–7.8×.
- Other options (Table 12): X-VLA FP32 → BF16 8.4× (Jetson); MolmoAct2 flow CUDA graphs 1.92×; fast modes that reuse or skip reasoning (MolmoAct2-Think reusing depth tokens 2.7×, DeepThinkVLA masking reasoning 16.8×) need their own task-success evaluation.
- Insight 2 (authors): kernel fusion and 4-bit weights give the largest gain but exist for two of 18 models and only on the Jetson, so inference software should bring them to more models and vendors, and model code should compile as one graph.

**Q3: what limits the optimized call (§5.3, Fig. 6, Appendix G, Table 15)**
- Analysed configurations: FlashRT with NVFP4 on the Jetson (π0.5 44 ms, GR00T N1.7 46 ms) and compilation on the AMD platform (347 ms, 258 ms). Ridge points: 947 / 1,894 / 3,791 FLOP per weight byte on the Jetson (FP16 / FP8 / NVFP4), 116 / 232 on the AMD platform (FP32 / BF16) (Fig. 6c,d).
- Action generation is memory-bound. A denoising step processes 10–41 tokens (action chunk plus robot state), so on the Jetson it does 20–150 operations per weight byte, far below the FP8 and NVFP4 ridges. FlashRT's steps take 1.6–1.8× the weight-read bound: GEMMs read weights at about three quarters of peak bandwidth, and short normalization, attention and quantization kernels add a third or more to the GEMM time. The paper calls this a hardware limit set by the few action tokens. On the AMD platform steps stay 2.8–3.3× above the bound, as compiled GEMMs use less bandwidth and Isaac-GR00T recomputes the context's keys and values in every step (FlashRT does it once per call).
- Prefill length decides its bound. π0.5's 574–712 prefix tokens put prefill near or above the ridge: compute-bound on the AMD platform but at only 42% of BF16 peak, with a fifth of its tokens being LeRobot's prompt padding (padded to 200 tokens); on the Jetson left of the ridge but 3.7× above the bound, as unfused attention and re-quantization take half its time. GR00T N1.7 prefills 156 tokens, is memory-bound and takes 1.7× its FP8 weight-read time on the Jetson; on the AMD platform its GEMMs read weights at a fifth of peak bandwidth.
- Vision encoding misses the matrix units on the AMD platform: LeRobot runs π0.5's tower in FP32, for which RDNA 3.5 has no matrix instructions, and ROCm's MIOpen runs GR00T N1.7's 3D patch embedding as 512 matrix-vector products, so the towers are 8× and 17× above the bound. On the Jetson, FlashRT's FP8 towers are memory-bound but 2.9–3.7× above the bound, as normalization, quantization and attention take a third to half their time.
- CPU preprocessing is the largest stage of GR00T N1.7 on the Jetson (39% of the fastest call); no optimization touches Isaac-GR00T's Python input processor and data collator. With PyTorch's 14 threads it takes 18.0 ms, with one thread 12.6 ms, and 2.3 ms on the AMD host (Fig. 6b). About a third goes to waking worker threads from the deepest idle state their cores enter while the GPU runs; the rest is serial work on one Arm core, which the AMD host does about 5× faster.

| Configuration      | Stage   | Format     | Time (ms) | F/P (ms) | W/B (ms) | Ratio |
| ------------------ | ------- | ---------- | --------- | -------- | -------- | ----- |
| Jetson, π0.5       | Vision  | FP8        | 5.66      | 0.88     | 1.51     | 3.7   |
| Jetson, π0.5       | Prefill | NVFP4, FP8 | 15.20     | 2.45     | 4.15     | 3.7   |
| Jetson, π0.5       | Action  | FP8        | 1.92      | 0.02     | 1.18     | 1.6   |
| Jetson, GR00T N1.7 | Vision  | FP8        | 4.61      | 0.72     | 1.58     | 2.9   |
| Jetson, GR00T N1.7 | Prefill | FP8        | 5.12      | 0.50     | 2.95     | 1.7   |
| Jetson, GR00T N1.7 | Action  | NVFP4      | 3.30      | 0.07     | 1.79     | 1.8   |
| AMD, π0.5          | Vision  | FP32       | 123.64    | 14.81    | 6.46     | 8.4   |
| AMD, π0.5          | Prefill | BF16       | 115.92    | 48.78    | 15.48    | 2.4   |
| AMD, π0.5          | Action  | BF16       | 8.09      | 0.12     | 2.49     | 3.3   |
| AMD, GR00T N1.7    | Vision  | BF16       | 99.51     | 5.88     | 3.16     | 16.9  |
| AMD, GR00T N1.7    | Prefill | BF16       | 49.79     | 5.92     | 8.72     | 5.7   |
| AMD, GR00T N1.7    | Action  | BF16       | 24.21     | 1.71     | 8.59     | 2.8   |

Table 15 (action per denoising step); Ratio = time over the larger of the two bounds.
- Insight 3 (authors): after optimization no single resource limits VLA inference; bandwidth limits few-token stages such as denoising on the Jetson, kernels limit vision encoding and prefill, and the host CPU limits preprocessing. Edge hardware needs bandwidth and a fast CPU more than peak compute, and inference software must fuse the kernels around the GEMMs and streamline preprocessing.

## Reading notes (inference)
Readers' inferences from a guided reading, not claims of the paper.
- **Iterations do not fully order latency.** §1 says latency "follows the number of iterations of action generation". Parallel decoders run a single iteration (N = 1), yet the fastest configuration is a flow-matching model (X-VLA, 77 ms on the Jetson, Table 7). Prefill and vision encoding are outside Eq. 2: OpenVLA-OFT's prefill (S3) alone takes 155 ms on the Jetson (Table 8). Reading: iteration count sets the order of magnitude, while the per-iteration cost t and the stages before S4 set the order within it. The per-step cost matters as much as the step count: the three flow-matching configurations that miss 50 ms per action (NORA-1.5, MolmoAct2 flow, InternVLA-A1.5) run about 10 steps each by (T − a)/b from Table 10, like π0.5, but combine small chunks (H = 5–10) with steps of 31–107 ms against π0.5's 14.7 ms. Insight 1 recommends cutting iterations and does not discuss t.
- **The keep-up test uses H, not the executed actions H_e.** §3.1 defines H as the actions "the controller executes before it calls the model again", and §3.2 tests T/H < 50 ms. Appendix Table 4 then lists an execution horizon H_e below H for two configurations: GR00T N1.7 (H = 16, H_e = 8) and VLA-0 (H = 8, H_e = 1). Fig. 2 draws the chunk as "H actions" of which the "First H_e" are executed, so the paper knows the distinction, but the text of §3 and §5.1 uses H throughout and does not discuss the mismatch (checked by searching the text for H_e and reading Fig. 2). Recomputed with H_e from Tables 4 and 7, the counts do not change: GR00T N1.7 takes 14.9 ms (Jetson) and 37 ms (AMD) per executed action, still under 50 ms; VLA-0 fails either way. So the issue is an inconsistent definition, not a changed result.
- **"Keeping up" depends on how execution overlaps inference, which the paper does not state.** With Δt = 50 ms: a throughput reading (actions produced per call vs consumed) gives T/H_e < Δt; overlapping inference where the next call starts as the executed actions begin also needs T ≤ H_e·Δt; overlapping inference that starts after H_e actions and covers the delay with the H − H_e leftover actions (as in real-time chunking) needs T ≤ (H − H_e)·Δt, which no configuration with H_e = H can meet. For the two configurations with H_e < H the verdict is the same under all three readings (GR00T N1.7: H_e = H − H_e = 8; VLA-0: 7 leftover actions, 899 ms each on the Jetson). On a real robot the world keeps moving during a call, so a late chunk acts on a stale observation and can lower task success. LIBERO evaluation scripts usually call the policy and then step the simulator, which pauses the world during inference (general knowledge, not checked against these releases). The LIBERO success that the releases report therefore does not include this latency penalty, and the paper's 20 Hz test is a stand-in for real-time operation, not a measured effect on success.
- **No task success is measured.** "Success" appears twice in the text (checked by search): the abstract notes that most VLA models report only task success, and Appendix F says the fast reasoning modes "need their own evaluation of task success". The effect of optimizations on behaviour is checked only by action agreement on 11 frames (cosine similarity and max |Δ|, Table 14), not by success; the effect of latency on success is not studied.
- **Longer chunks trade latency for staleness.** Insight 1 lists longer action chunks as a way to keep up, since T/H falls as H grows. A longer chunk also runs open loop for longer, so its later actions rest on an older observation; the paper does not discuss this cost, and its benchmark (one fixed observation, no closed loop) cannot measure it.
- **For π0.5, the low-precision gain is mostly FP8, not 4-bit.** In π0.5's NVFP4 configuration only the language model's FFN uses NVFP4 (Appendix G), and NVFP4 adds 1.08× over FP8 (47.9 → 44.4 ms, Table 12), against 1.34× for GR00T N1.7, whose action head is all NVFP4. Insight 2's "4-bit weights" fits GR00T N1.7 better than π0.5.
- **Each optimization level also changes number formats.** Compilation switches π0.5's FP32 matmuls to TF32, and FlashRT runs its FP32 layers in FP16 (§5.2). The per-level speed-ups therefore mix kernel fusion or graph capture with precision changes, and the paper does not separate them.
- **The "fast host CPU" recommendation rests on a software problem in one model.** CPU preprocessing dominates only GR00T N1.7's optimized call; π0.5's is small (Fig. 6a). About a third of GR00T N1.7's 18.0 ms is thread wake-up that one thread removes (12.6 ms), and the rest is serial Python in Isaac-GR00T's input processor and data collator, which no optimization in the study touched. Insight 3 turns this into a hardware requirement before the software fix is tried.

## Related
See also: [Jung et al. VLA workload characterization](vla-workload-characterization-kaist.md), another batch-size-1 characterization that also measures π0.5, GR00T and OpenVLA-OFT on Jetson Thor.
