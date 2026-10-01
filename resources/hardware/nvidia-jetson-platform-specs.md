---
type: entity
tags: [hardware, jetson-orin, jetson-thor, specs, first-party, community]
sources: [https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/, https://developer.nvidia.com/blog/introducing-nvidia-jetson-thor-the-ultimate-platform-for-physical-ai/, https://forums.developer.nvidia.com/t/real-time-inference-on-thor-rtx-pi0-5-gr00t-n1-6-1-7-thor-23-hz-rtx-5090-50-80hz/368788]
---
# NVIDIA Jetson Orin and Thor: vendor specs and community VLA numbers

## Summary
Jetson Orin and Thor are the edge platforms almost every "edge VLA" paper in this wiki uses. Vendor headline TOPS are sparse INT8/FP4 figures, and the memory bandwidth (LPDDR) is the more relevant limit for VLA action experts. This note records the figures from NVIDIA's pages as extracted (the fetch tool summarizes pages, so re-check the datasheet before relying on a number).

## Details
- **Orin Nano 4 GB / 8 GB:** 34 / 67 sparse INT8 TOPS; 4 GB 64-bit / 8 GB 128-bit LPDDR5; 51 / 102 GB/s; power modes 7–15–25 W.
- **Orin NX 8 GB / 16 GB:** 117 / 157 sparse INT8 TOPS; 128-bit LPDDR5; 102.4 GB/s; 10–40 W.
- **AGX Orin 32 GB / 64 GB:** 248 / 275 TOPS (page labels the family sparse INT8); 256-bit LPDDR5; 204.8 GB/s; 15–60 W.
- **AGX Thor:** 2070 FP4 TFLOPS (sparse); 1035 TFLOPS dense FP4 or sparse FP8/INT8; 517 TFLOPS dense FP8 or sparse FP16; 128 GB 256-bit LPDDR5X at 273 GB/s; 40–130 W. NVIDIA's page reports GR00T N1.5 at "41.5" output tokens per second on Thor, 2.74× AGX Orin (units as printed).
- **Dense vs sparse:** the page figures are quoted sparse; dense throughput is lower (about half for 2:4 structured sparsity, an inference, not stated on the page). Papers in this wiki quote dense BF16 numbers that differ by 2× or more for the same device (AGX Orin 42 vs 100 TFLOPS in [XPU characterization](../serving/vla-xpu-characterization.md) and [edge bottleneck characterization](../serving/vla-edge-bottleneck-characterization.md)); state precision and sparsity whenever citing.
- **Community measurements (forum thread, unofficial):** a community developer using hand-written CUDA kernels reported on Thor: π0.5 44 ms (23 Hz), π0 46 ms (22 Hz), GR00T N1.6 41–45 ms; on an RTX 5090: π0.5 17.6 ms. Precision, camera count and denoising steps were not given, so these cannot be compared with BF16 roofline or PyTorch numbers (for scale: VLA-Perf's BF16 roofline for π0 with three cameras on Thor is 52.6 ms, and [Jetson-PI](../serving/jetson-pi.md) measured 309–458 ms for π0.5 in PyTorch/llama.cpp variants). Treat as an existence proof that heavy kernel work and lower precision can move Thor by an order of magnitude.
- **Trust level:** vendor specs are reliable for what they state; the forum numbers are a single unreviewed post.

See also: [Sub-20-TOPS parts](edge-accelerator-datasheets.md), [XPU study](../serving/vla-xpu-characterization.md), [VLA-Perf](../serving/vla-perf.md).
