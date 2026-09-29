---
type: entity
tags: [hardware, rk3588, rockchip, npu, third-party, specs]
sources: [https://turingpi.com/rk3588-architecture-cpu-gpu-npu-memory/, https://tinycomputers.io/posts/rockchip-rk3588-npu-benchmarks.html]
---
# Rockchip RK3588: SoC and NPU facts

## Summary
The RK3588 is an 8-core Arm SoC (4× Cortex-A76 + 4× Cortex-A55) with a three-core NPU rated at "up to 6 TOPS" and a 64-bit LPDDR interface shared by CPU, GPU and NPU. It is the most common low-cost board for robot prototypes (Orange Pi 5, Radxa Rock 5, Firefly, Turing Pi RK1 and others). This note collects the figures from two third-party write-ups; the vendor datasheet was not read, and the fetch tool summarizes pages, so re-check figures against Rockchip's documents before relying on them.

## Details
- **NPU:** three cores, "6 TOPS total" (2 TOPS per core); supported types listed as INT4, INT8, INT16, FP16, BF16 and TF32 (Turing Pi); the headline 6 TOPS is an INT8 figure ("optimized for INT8", tinycomputers). FP16 throughput is not stated in these sources. Turing Pi lists 1 MB of shared on-chip NPU memory.
- **Memory:** four 16-bit LPDDR channels (64-bit total), LPDDR4, LPDDR4X or LPDDR5, up to 32 GB. Measured CPU-side STREAM bandwidth about 21–22 GB/s (block copy 17–19 GB/s, memcpy 8–9 GB/s); with two concurrent sessions each got 60–65% of single-session throughput and with three about 40–50% (Turing Pi). Speed grade and board were not the same across tests.
- **Power:** an estimated 5–6 W under AI load on an Orange Pi 5 Max (16 GB LPDDR5), from an estimate, not a meter reading (tinycomputers).
- **Sizing limits stated:** models above about 2 GB may not fit; conversion needs an x86_64 host; dynamic shapes carry overhead; "TOPS does not guarantee that an entire neural network maps to the accelerator" (Turing Pi).
- **Reference measurements from the same sources:** ResNet-18 INT8 4.09 ms (244 FPS) and about 49 FPS/W (tinycomputers); RKLLM on RK3588 supports W8A8 only, with W4A16 unavailable ([toolchain note](rockchip-rknn-rkllm-toolchain.md) confirms W8A8 for RK3588 benchmarks).
- **Compared with the wiki's other devices:** the measured 21–22 GB/s (CPU STREAM) and the 24–30 GB/s implied by NPU decode ([measurements](rk3588-vlm-llm-measurements.md)) compare with peak figures of 204.8 GB/s for AGX Orin and 51.2 GB/s for the Ascend 310B; the practical figure is what matters for VLA expert loops ([edge hardware note](../knowledge/edge-hardware-and-the-10-tops-gap.md)).
- **Trust level:** third-party blogs; useful for orders of magnitude.

See also: [Rockchip toolchain](rockchip-rknn-rkllm-toolchain.md), [RK3588 VLM/LLM measurements](rk3588-vlm-llm-measurements.md), [sub-20-TOPS parts](edge-accelerator-datasheets.md).

See also: [Unitree compute](unitree-robot-compute.md), [AgiBot compute](agibot-robot-compute.md) for robots that use this SoC.
