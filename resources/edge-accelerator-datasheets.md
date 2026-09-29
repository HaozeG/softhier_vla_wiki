---
type: entity
tags: [hardware, npu, hailo, raspberry-pi, ascend, specs]
sources: [https://hailo.ai/products/ai-accelerators/hailo-10h-ai-accelerator/, https://www.raspberrypi.com/products/ai-hat/, arxiv:2604.24447]
---
# Sub-20-TOPS edge accelerators: what the vendor pages state

## Summary
The "about 10 TOPS" class includes NPUs such as Hailo's and Ascend's small parts and single-board computers. Vendor pages give TOPS but rarely memory bandwidth, and no source in this wiki reports a VLA running on a Hailo or Raspberry Pi AI HAT+ NPU (the one 10 TFLOP/s NPU with data is the Ascend 310B, for ACT only). This note lists the figures found so the gap is explicit.

## Details
- **Raspberry Pi AI HAT+:** 13 TOPS variant with a Hailo-8L accelerator and 26 TOPS variant with a Hailo-8, for the Raspberry Pi 5 (HAT+ interface). The page does not state the precision behind the TOPS figures.
- **Hailo-10H:** "40 | 20 TOPS (INT4 | INT8)", 2.5 W typical, LPDDR4/4X interface, marketed for LLMs, VLMs and generative AI. No VLA numbers on the page.
- **Huawei Ascend 310B:** 10 TFLOP/s FP16, 12 GB, 51.2 GB/s (from the leaderboard hardware table in [VLA XPU characterization](vla-xpu-characterization.md)); classified there as a "Basic" tier device that can run only small VLAs (for example SmolVLA-sized), not 7B models.
- **Raspberry Pi 5 CPU (no NPU):** measured SmolVLA at 8.19 s per 50-action chunk and a 60M ACT-style policy at 33.5 actions/s ([vla.simd](vla-simd.md)).
- **Rockchip RK3588:** 6 TOPS NPU (3 cores) with a 64-bit LPDDR interface; see [RK3588 platform](rk3588-platform-specs.md) and [RK3588 deployment](../knowledge/rk3588-vla-deployment.md).
- **Precision caveat:** INT4/INT8 TOPS are not comparable to BF16 TFLOPS. A VLA that needs BF16 attention or a floating-point flow loop cannot use the INT4 figure.
- **Gap:** no flow-matching VLA was found measured on a 10-TOPS-class NPU (Hailo, Rockchip, Ascend 310B) in the sources ingested here. The nearest data are ACT on the Ascend 310B (about 10 Hz, plot-read) and SmolVLA on the 88 TFLOP/s Ascend 310P (about 2 Hz) in [XPU characterization](vla-xpu-characterization.md). See [edge hardware and the 10 TOPS gap](../knowledge/edge-hardware-and-the-10-tops-gap.md).

See also: [Jetson specs](nvidia-jetson-platform-specs.md), [vla.simd](vla-simd.md).
