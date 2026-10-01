---
type: paper
tags: [runtime, ggml, llama-cpp, edge, jetson-orin-nano, quantization, recent]
sources: [arxiv:2606.08094, https://arxiv.org/abs/2606.08094]
---
# vla.cpp: A Unified Inference Runtime for Vision-Language-Action Models

Nguyen, Ho, Nguyen, Duong, Le, Nguyen, Ngo, Le (VinRobotics, VinUniversity, TU Darmstadt and others), arXiv 2606.08094 (v2, Sept 2026). Recent paper.

## Summary
vla.cpp is a C++ inference runtime (built on ggml/llama.cpp, GGUF weights, no PyTorch at run time) for eleven VLAs, including SmolVLA, π0, π0.5, GR00T N1.5–N1.7, OpenVLA-OFT and BitVLA. It targets CUDA, Metal, CPU, SYCL and OpenVINO backends. It contributes a broad deployment survey: latency on RTX 3060/3090, Apple M4, Intel Arc, Jetson AGX Orin and the 8 GB Jetson Orin Nano, quantization studies, and numerical-validation lessons.

## Key claims
- **Design (§III):** observation tokens form a prefix whose features are reused across solver steps within a request; latency model L(T) ≈ P + T·E for prefix cost P and per-step expert cost E. Graphs and buffers persist across requests. Server and client communicate over ZeroMQ + Protobuf.
- **Success vs references (Table I, LIBERO-Object, 100 episodes):** ten of eleven models within 3.2 points of reference (GR00T-N1.6 88% vs 99%, unresolved). SmolVLA 96%, π0 82%, π0.5 96%, BitVLA 100%.
- **Jetson Orin Nano 8 GB (Table III, client time per executed action incl. transport):** SmolVLA (S=4) 141.8 ms with 176/200 success; BitVLA (S=8) 355.7 ms, 200/200; Evo-1 458.8 ms; GR00T-N1.6/N1.7 out of memory. The SmolVLA horizon sweep on Orin Nano (Fig. 5, H=50, inference excluding transport) gives median 358–457 ms per chunk.
- **AGX Orin / RTX 3060:** SmolVLA 65.4 / 28.2 ms per action; BitVLA 101.1 / 37.9 ms.
- **CPU and other devices:** on an 8-thread i9-14900HX, SmolVLA returns actions in 2141 ms and π0 in 7888 ms; Apple M4 Metal: SmolVLA 374 ms, π0 1164 ms, GR00T-N1.7 539 ms; Intel Arc A380 (SYCL) cuts SmolVLA from 1920 to 630 ms vs its host CPU.
- **Versus PyTorch (Table IV, RTX 3090):** SmolVLA 55.8 ms vs eager 174.1 / compiled 65.9 ms; π0 97.9 vs 99.4 / 99.7; speedup 1.0–1.84× vs the faster PyTorch mode. TensorRT was 1.85× faster than vla.cpp for GR00T-N1.7 on an RTX PRO Blackwell (70.5 vs 130.2 ms).
- **Ternary kernels (§IV-D):** BitVLA's ternary weights packed to 1.34 GiB (from 5.6 GiB); switching the CUDA-core dp4a path to tensor-core IMMA cut time per executed action from 172.8 to 37.85 ms (RTX 3060) and from 406.6 to 101.11 ms (AGX Orin), 4.57× and 4.02×. Packing alone leaves latency unchanged.
- **GGUF quantization (Table V, GR00T-N1.7, RTX 3060):** Q4_0 with vision quantized: 4556 MB vs 6292 MB BF16, speedup only 1.14×, success 195/200 vs 196/200. Fixed-input action error did not predict task success.
- **Solver steps (Table VI, GR00T-N1.7, RTX 3060):** vision fixed at about 18.7 ms; backbone plus head 19.6 → 107.5 ms for T = 1 → 16, fitting 13.9 + 5.8T ms. Success stayed 95–99/100 across T; at T = 1 the maximum action difference from T = 4 was 0.93.
- **Where time goes (RTX 5070, §IV-E):** SmolVLA vision 38% + backbone 14%; π0 vision 21% + backbone 54%; the action expert takes nearly half of SmolVLA and GR00T-N1.6 time even with cached features. Roofline ridge points: 71 (RTX 3060) and 104 FLOP/byte (AGX Orin); prefix intensity 256–530, expert about 50.
- **Numerical pitfall (§IV-F):** computing SmolVLA vision positional indices at the wrong precision moved patch coordinates across an index boundary, dropping LIBERO-Object task-0 success from 9/10 to 2/10 with a gripper-channel action error of about 1.97.

## Relevance to SoftHier-VLA
The most useful public data for sub-Thor devices, including SmolVLA on an 8 GB Orin Nano and CPU-only latencies. It also demonstrates that weight-only quantization brings small speedups (1.08–1.14×) unless there is a native low-bit datapath, and that discrete preprocessing (index precision) must be validated. See [edge hardware and the 10 TOPS gap](../../knowledge/edge-hardware-and-the-10-tops-gap.md), [quantization](../../knowledge/quantization.md) and [serving methods](../../knowledge/serving-methods.md).

See also: [vla.simd](vla-simd.md) (same group, CPU), [Jetson-PI](jetson-pi.md), [BitVLA](../compression/bitvla.md), [VLA-Perf](vla-perf.md), [LiteVLA-Edge](litevla-edge.md).
