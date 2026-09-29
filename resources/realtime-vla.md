---
type: paper
tags: [inference-optimization, cuda-graph, kernel-fusion, roofline, pi0, rtx-4090]
sources: [arxiv:2510.26742, https://arxiv.org/abs/2510.26742, https://github.com/Dexmal/realtime-vla]
---
# Running VLAs at Real-time Speed (Realtime-VLA)

Ma, Zhou, Yang, Wang, Fan (Dexmal, StepFun), arXiv 2510.26742 (Oct 2025).

## Summary
A systems paper showing that a π0-class VLA can run at camera frame rate on one RTX 4090 by eliminating overheads: CUDA graphs, graph simplification (constant folding, QKV fusion), tuned Triton GEMM tiles, fused gated linears and scalar ops. It reaches within about 30% of a roofline lower bound it derives, and proposes a "full streaming" mode that overlaps the compute-bound VLM with the memory-bound action expert.

## Key claims
- **Latency (Table 1, RTX 4090, empty prompt, chunk 63, BF16):** naive PyTorch 105.0 / 106.5 / 113.9 ms; openpi/JAX 43.8 / 53.7 / 67.6 ms; this work 20.0 / 27.3 / 36.8 ms for 1 / 2 / 3 views.
- **Step contributions (Fig. 2, 2 views):** CUDA graph 106.5 → 43.5 ms (about 2×, no dynamic branches so the graph can be recorded); graph simplification → 35.7 ms; optimized kernels → 27.3 ms; roofline 20.6 ms.
- **Graph transformations (§3.2):** fold RMSNorm affine weights into the next linear layer; fold the action/time embedding linear layers (time branch tabulated for the 10 timesteps and fused into the bias); fuse Q/K/V and RoPE into one matmul. Saves 7–8 ms. The LLM runs 17 not 18 layers before the expert because the last layer's KV is not needed.
- **Kernel tuning (§4, Table 2):** π0 decomposes into 24 GEMM shapes; vision encoder and LLM are compute-bound, the action expert is bandwidth-bound; 128 SMs vs 144 tiles motivated a partial split-K.
- **Roofline (§5):** lower bound 12.8 / 19.7 / 26.7 ms (13.7 / 20.6 / 27.6 ms with a 0.86 ms synchronization allowance) using 1.01 TB/s and 91.4 TMAC/s. There are 1378 matmuls per inference; inter-kernel overhead is 12.92 ms in PyTorch, 1.72 ms with a CUDA graph, 0.86 ms with a software grid barrier.
- **Overlap (§6.1):** running the 10 action-expert steps concurrently with a VLM pass takes 26.3 ms vs 27.3 ms sequential, and up to 16 expert runs fit in 33 ms, motivating the claimed 30 Hz / 480 Hz "trajectory frequency" design. The paper itself distinguishes trajectory density from control frequency.
- **Real-world test (§1):** 100% success on a falling-pen catch task with π0; a small proof of concept.
- **Future work (§9):** low-precision quantization (all results use BF16), 60–120 FPS, 7B models.

## Relevance to SoftHier-VLA
Shows how much of VLA latency on a GPU is launch and synchronization overhead (about 4× between naive and tuned), and provides the per-GEMM shape list of π0 that a many-PE mapping must schedule. See [inference workload characterization](../knowledge/inference-workload-characterization.md). It is the source the [VLA-Perf](vla-perf.md) roofline is validated against.

See also: [FlashVLA](flashvla-streaming.md), [Jetson-PI](jetson-pi.md), [π0](pi0.md).
