---
type: entity
tags: [robot-controller, brain-cerebellum, rk3588, secondary, vendor-blog]
sources: [https://www.globenewswire.com/news-release/2025/10/09/3164034/28124/en/China-and-Global-Robot-Controllers-Brain-Cerebellum-Research-Report-2025-Brain-Cerebellum-Integration-Becomes-a-Trend-and-Automotive-Grade-Chips-Migrate-to-Robots.html, https://www.dusuniot.com/blog/rk3588-robot-control-board/]
---
# Robot controller architecture: a market-report press release and a vendor blog

## Summary
Two secondary sources describe how robot makers divide compute. A market-research press release defines a "brain" (perception, planning, decision, interaction, learning) and a "cerebellum" (motion control, coordination, feedback regulation, stability) and lists chips per company. A board vendor's blog argues for an RK3588-based control board. Neither is primary documentation; use them for vocabulary and pointers.

## Details
- **Partition definition (press release for a research report):** the brain "processes multi-modal sensory data using AI algorithms"; the cerebellum has "extremely high determinism and low-latency requirements". The release says brain and cerebellum integration is becoming a trend.
- **Examples listed:** Unitree A2 (Aug 2025): brain Intel Core i7 for secondary development and AI deployment, cerebellum an 8-core CPU. AgiBot Lingxi X2 (Mar 2025): two RK3588 (6 TOPS each) with an Orin NX (157 TOPS) on the flagship, all described as brain (conflicting with the vendor page's motion-control statement, see [AgiBot compute](agibot-robot-compute.md)). Fourier N1 (Apr 2025): Intel Core i7-13700H. D-Robotics RDK S100 (Jun 2025): brain = CPU (6 Arm cores) plus an 80 TOPS BPU, cerebellum = four Cortex-R52+ MCU cores for low latency. SemiDrive D9-Max (May 2025): 12 Cortex-A55, dual-core lockstep Cortex-R5F, 8 TOPS NPU, 115 GFLOPS GPU.
- **RK3588 control-board blog (Dusun IoT, vendor):** CPU for general control and data processing (about 93K DMIPS claimed), NPU for inference (YOLOv8n at 59.6 fps), Mali GPU for vision, CAN for actuators, up to eight MIPI camera inputs, RGMII Ethernet for LiDAR, PCIe 3.0. It mentions an asymmetric multiprocessing design for real-time behaviour but describes no separate MCU and does not address Linux real-time limits.
- **Trust level:** low to medium; the release summarizes a paid report and the blog is a product pitch. The chip lists cannot be checked against the report itself.

See also: [Unitree compute](unitree-robot-compute.md), [AgiBot compute](agibot-robot-compute.md), [RK3588 platform](../rk3588/rk3588-platform-specs.md), [robot compute partitioning](../../knowledge/robot-compute-partitioning.md).
