---
type: comparison
tags: [inference, mfu, roofline, utilization, batch-1, edge, jetson, amd, quantization]
sources: [resources/serving/vla-hwbench-edge-latency.md, resources/serving/vla-xpu-characterization-sjtu.md, resources/serving/vla-workload-characterization-kaist.md]
---
# MFU of VLA stages, computed from published measurements

How much of a chip's peak does each stage of a VLA call use, by model, platform and optimization? This note keeps one running table, filled from sources that report a stage's operation count, its measured time and the platform's peak.

**Label: `inference`** ([wiki-design 0013](../wiki-design/decisions/0013-scope-and-no-derived-content.md)). The user asked for this table. Every MFU and bandwidth-utilization value below is our arithmetic on numbers a source reports; no source prints these percentages. The inputs (F, W, time, peak) are the source's own and are labelled by its evidence tier. Rows are added on request, not in routine upkeep.

## Summary
- **Definition used.** MFU (model FLOPs utilization) = F / (t · P): the stage's floating-point operations F, divided by its measured time t and the platform's peak P in the stage's number format. Bandwidth utilization = W / (t · B), with W the bytes the source counts and B the peak memory bandwidth.
- **What the first rows show** (VLA-HWBench, the fastest configuration on each platform, batch 1):
  - Long-sequence stages (vision tower, π0.5 prefill) reach 10–28% MFU on Jetson Thor with FlashRT and 6–42% on the AMD Ryzen AI Max+ 395 with `torch.compile`.
  - Denoising steps reach 0.7–7% MFU. They are memory-bound, so MFU is the wrong yardstick for them: their bandwidth utilization is 54–61% on Thor and 31–35% on AMD.
- **Only one source feeds the table so far.** The other serving sources in the wiki give roofline positions or SM utilization, not F and t per stage (see Sources not yet usable).

```text
source reports, per stage           we compute
+-------------------------+
| F    GFLOP              |---+
| W    bytes (weights)    |   |   MFU     = F / (t * P)
| t    measured time      |---+-> BW util = W / (t * B)
| P, B peak FLOP/s, B/s   |   |   achieved TFLOP/s = F / t
|      (state whose peak) |---+
+-------------------------+
one row = one (platform, model, stage, software, number format)
```

## Comparison
VLA-HWBench Table 15 ([source](../resources/serving/vla-hwbench-edge-latency.md)), measured. Peaks are the paper's Table 3: Thor FP8 517, NVFP4 1,035 TFLOP/s, 273 GB/s; AMD BF16 59.4, FP32 29.7 TFLOP/s (derived by the paper from CU count and clock), 256 GB/s. Thor runs FlashRT (fused kernels, CUDA graphs, FP8 or NVFP4 weights). AMD runs `torch.compile` max-autotune: for π0.5 on FlashRT's workload (10 actions, two image slots), for GR00T N1.7 on the action head only, as in the Isaac-GR00T recipe. Action rows are per denoising step. W counts weight bytes only, so bandwidth utilization is a lower bound.

| Platform    | Model      | Stage        | Software               | Format     | t (ms) | F (GFLOP) | Achieved TFLOP/s | Peak used (TFLOP/s) | MFU   | Achieved GB/s | BW util | Bound (source)             |
| ----------- | ---------- | ------------ | ---------------------- | ---------- | ------ | --------- | ---------------- | ------------------- | ----- | ------------- | ------- | -------------------------- |
| Jetson Thor | π0.5       | vision       | FlashRT                | FP8        | 5.66   | 439.7     | 77.7             | 517 (FP8)           | 15.0% | 73            | 27%     | memory, 3.7× above bound   |
| Jetson Thor | π0.5       | prefill      | FlashRT                | NVFP4, FP8 | 15.20  | 2205.4    | 145.1            | 517 (FP8)           | 28.1% | 74            | 27%     | memory, 3.7× above bound   |
| Jetson Thor | π0.5       | prefill      | FlashRT                | NVFP4, FP8 | 15.20  | 2205.4    | 145.1            | 1,035 (NVFP4)       | 14.0% | 74            | 27%     | memory, 3.7× above bound   |
| Jetson Thor | π0.5       | action, step | FlashRT                | FP8        | 1.92   | 7.1       | 3.7              | 517 (FP8)           | 0.7%  | 168           | 61%     | memory, 1.6× above bound   |
| Jetson Thor | GR00T N1.7 | vision       | FlashRT                | FP8        | 4.61   | 349.5     | 75.8             | 517 (FP8)           | 14.7% | 93            | 34%     | memory, 2.9× above bound   |
| Jetson Thor | GR00T N1.7 | prefill      | FlashRT                | FP8        | 5.12   | 254.4     | 49.7             | 517 (FP8)           | 9.6%  | 157           | 58%     | memory, 1.7× above bound   |
| Jetson Thor | GR00T N1.7 | action, step | FlashRT                | NVFP4      | 3.30   | 69.8      | 21.2             | 1,035 (NVFP4)       | 2.0%  | 148           | 54%     | memory, 1.8× above bound   |
| AMD 395     | π0.5       | vision       | compile (max-autotune) | FP32       | 123.64 | 439.7     | 3.6              | 29.7 (FP32)         | 12.0% | 13            | 5%      | compute, 8.4× above bound  |
| AMD 395     | π0.5       | prefill      | compile (max-autotune) | BF16       | 115.92 | 2896.8    | 25.0             | 59.4 (BF16)         | 42.1% | 34            | 13%     | compute, 2.4× above bound  |
| AMD 395     | π0.5       | action, step | compile (max-autotune) | BF16       | 8.09   | 7.3       | 0.9              | 59.4 (BF16)         | 1.5%  | 79            | 31%     | memory, 3.3× above bound   |
| AMD 395     | GR00T N1.7 | vision       | compile, head only     | BF16       | 99.51  | 349.5     | 3.5              | 59.4 (BF16)         | 5.9%  | 8             | 3%      | compute, 16.9× above bound |
| AMD 395     | GR00T N1.7 | prefill      | compile, head only     | BF16       | 49.79  | 351.5     | 7.1              | 59.4 (BF16)         | 11.9% | 45            | 18%     | memory, 5.7× above bound   |
| AMD 395     | GR00T N1.7 | action, step | compile, head only     | BF16       | 24.21  | 101.4     | 4.2              | 59.4 (BF16)         | 7.1%  | 91            | 35%     | memory, 2.8× above bound   |

Cross-checks against the source's own statements: π0.5 prefill on AMD at 42.1% matches the paper's "42% of BF16 peak"; Thor action-step GEMMs reading weights at "three quarters of peak bandwidth" is consistent with 54–61% for the whole step, which also includes normalization, attention and quantization kernels. The "Bound" column is the source's Ratio (time over the larger of F/P and W/B).

## Sources not yet usable
| Source                                                                             | What it reports                                                                                                       | Why no row                                                                       |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [Jung et al. (KAIST)](../resources/serving/vla-workload-characterization-kaist.md) | Roofline points per stage on RTX 4090 (figure), stage latency                                                         | F per stage not given in the source note; points are read from a figure          |
| [Zhou et al. (SJTU)](../resources/serving/vla-xpu-characterization-sjtu.md)        | SM utilization of π0 per phase on RTX 4090, Orin, Thor                                                                | SM utilization counts busy SMs, not FLOPs; it is not MFU                         |
| VLA-Perf (NVIDIA, arXiv 2602.18397), not ingested                                  | Modeled roofline latency on five GPUs; Table 1 measured 73–83% of roofline for Triton π0 on RTX 4090                  | Modeled values assume 100% of roofline; one measured point, as roofline fraction |
| Waseem & Ali-Eldin (Chalmers, arXiv 2611.06710), not ingested                      | Measured bf16 GEMM peak and DRAM bandwidth for H100 NVL, A10G, Thor, RTX 4090; stage throughput on rooflines (figure) | Per-stage values only in a figure                                                |

## Caveats
- **Peaks differ between papers.** For Jetson Thor's 16-bit peak, the papers above use 258 (VLA-HWBench), 400 (VLA-Perf) and 153 TFLOP/s measured (Chalmers); one more paper (Google/Purdue, arXiv 2603.02271, not ingested) uses 500. Each row therefore states its peak; rows from different papers are comparable only after re-normalizing to one peak.
- **Mixed-format stages have no single peak.** π0.5 prefill on Thor runs NVFP4 FFNs and FP8 elsewhere, so it is listed against both peaks.
- **W is weight bytes only** in VLA-HWBench, so activation and KV traffic are missing and bandwidth utilization is understated.
- **Software matters as much as the chip.** The AMD vision rows are low because LeRobot runs π0.5's tower in FP32 without matrix instructions and MIOpen runs GR00T N1.7's patch embedding as matrix-vector products ([source](../resources/serving/vla-hwbench-edge-latency.md)); a row describes a (chip, software) pair, not the chip alone.

## Open questions
- Which further sources report F and t per stage, so that an RTX 4090, H100 or NPU row can be added? Candidates: ingest Chalmers and VLA-Perf, or compute F from model configs (that would be a second layer of inference, to be agreed first).
- Should reference (unoptimized) configurations get rows too, so that the MFU gain from each optimization step shows directly? VLA-HWBench reports F and t per stage only for the fastest configurations.
