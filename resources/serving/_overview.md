---
covers: d97ea5ed1052
---
# resources/serving/

Sources on running VLAs: latency models, runtimes, async chunk execution and measured profiles on GPUs, Jetsons and CPUs.

- [Embodied.cpp](embodied-cpp.md) — C++ runtime, 4-bit π0.5 drops
- [FlashVLA](flashvla-streaming.md) — streaming action decoding
- [Jetson-PI](jetson-pi.md) — π0.5 on Orin and Thor
- [LeRobot async docs](lerobot-async-inference-docs.md) — client/server settings
- [LiteVLA-Edge](litevla-edge.md) — 256M 4-bit, latency only
- [RTC](real-time-chunking.md) — inpainting for async chunks
- [Realtime-VLA](realtime-vla.md) — π0 at 27 ms on a 4090
- [vla.cpp](vla-cpp.md) — 11-model runtime, Orin Nano
- [Edge bottleneck study](vla-edge-bottleneck-characterization.md) — decode-bound
- [VLA-Perf](vla-perf.md) — roofline latency model
- [vla.simd](vla-simd.md) — CPU inference, Pi 5
- [XPU study](vla-xpu-characterization.md) — cross-device leaderboard
