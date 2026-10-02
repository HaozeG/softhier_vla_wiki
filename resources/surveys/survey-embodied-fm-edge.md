---
type: paper
tags: [survey, edge, deployment, npu, unified-memory, recent]
sources: [arxiv:2603.16952, https://arxiv.org/abs/2603.16952]
---
# Embodied Foundation Models at the Edge: A Survey of Deployment Constraints and Mitigation Strategies

Grover, Ranjan, Mao, Dong, Praveen, Wu, Chang, Mohsenin, Sheng, Polyzou, Kanjo, Lin (USF, FIU and others), arXiv 2603.16952 (v2, Mar 2026). Secondary source; recent.

## Summary
A survey that frames edge deployment of embodied foundation models as a systems problem organized into eight coupled barriers (the "Deployment Gauntlet"). Its claims relevant to NPU-class devices are operator-coverage gaps, heterogeneous-compute penalties, unified-memory contention and thermal limits. It cites numbers from other papers; none were checked here, and it does not discuss Rockchip parts.

## Key claims
- **Workload split (abstract):** autoregressive VLA policies are constrained mainly by memory bandwidth, diffusion-based controllers more by compute latency and sustained execution cost.
- **Operator coverage (§3.2.1):** edge NPUs accelerate a narrow set of dense kernels (for example INT8 matrix multiplication); unsupported operators force graph partitioning and CPU fallback, creating execution bubbles. NanoVLA is cited as improving throughput up to 1.7× by removing small CPU-resident operators.
- **Launch overhead (§3.2.2):** on Jetson Orin, CPU-side launch overhead can be 30–60% of latency in autoregressive decoding (cited); sequential token generation can hold utilization below 20%.
- **Unified memory (§3.2.3, §3.3):** CPU, GPU, NPU and sensor DMA share LPDDR channels, so inference competes with perception traffic; moving high-resolution features between CPU and NPU can add 4–15 ms (cited).
- **Thermal (§3.2.4, §3.4):** mixed-workload saturation was reported to cut steady-state throughput by up to 60% against cold start (cited); an extra 10–15 W of accelerator load can cost a drone several minutes of endurance.

## Related
See also: [Yu et al.](survey-efficient-vla-yu.md), [edge bottleneck study](../serving/vla-edge-bottleneck-characterization.md).
