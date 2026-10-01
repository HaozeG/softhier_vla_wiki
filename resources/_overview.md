---
covers: 7653efc1f0c0
---
# resources/

One faithful note per source, cited by the knowledge notes. Tags `recent`, `low-evidence`, `first-party`, `community` mark evidence tier ([decision 0004](../memories/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md)).

**Models**
- [RT-2](rt-2.md) — first VLA; 55B cloud-served at 1–3 Hz
- [OpenVLA](openvla.md) — open 7B discrete-token VLA; LoRA, int4
- [Octo](octo.md) — 27–93M diffusion-head generalist policy
- [π0](pi0.md) — PaliGemma + 300M flow expert; latency table
- [π0.5](pi05.md) — co-training, hierarchical inference
- [FAST](fast-tokenizer.md) — DCT+BPE action tokens
- [OpenVLA-OFT](openvla-oft.md) — parallel decoding + chunking, 26×
- [GR00T N1](gr00t-n1.md) — dual-system 2.2B, 4-step DiT
- [SmolVLA](smolvla.md) — 450M VLA, async inference
- [TinyVLA](tinyvla.md) — sub-1.5B, diffusion head

**Surveys**
- [Yu et al.](survey-efficient-vla-yu.md) — efficient VLAs, lifecycle view
- [Guan et al.](survey-efficient-vla-guan.md) — efficient VLAs, pipeline view
- [Ma et al.](survey-vla-embodied-ai-ma.md) — VLA components, policies, planners
- [Zhong et al.](survey-vla-action-tokenization.md) — eight action-token types

**Serving and systems**
- [VLA-Perf](vla-perf.md) — roofline latency model
- [Realtime-VLA](realtime-vla.md) — π0 at 27 ms on a 4090
- [RTC](real-time-chunking.md) — inpainting for async chunks
- [FlashVLA](flashvla-streaming.md) — streaming action decoding
- [Jetson-PI](jetson-pi.md) — π0.5 on Orin and Thor
- [vla.cpp](vla-cpp.md) — 11-model runtime, Orin Nano
- [vla.simd](vla-simd.md) — CPU inference, Pi 5
- [LiteVLA-Edge](litevla-edge.md) — 256M 4-bit, latency only
- [Edge bottleneck study](vla-edge-bottleneck-characterization.md) — decode-bound
- [XPU study](vla-xpu-characterization.md) — cross-device leaderboard
- [Embodied.cpp](embodied-cpp.md) — C++ runtime, 4-bit π0.5 drops
- [Edge survey](survey-embodied-fm-edge.md) — operator gaps, shared DRAM

**Compression**
- [VLA-Cache](vla-cache.md) — temporal token caching
- [LightVLA](lightvla.md) — learned token pruning
- [EfficientVLA](efficientvla.md) — layers + tokens + cache
- [DeeR-VLA](deer-vla.md) — early exit
- [DySL-VLA](dysl-vla.md) — dynamic-static layer skipping
- [CLP](clp-layer-pruning.md) — CKA layer pruning
- [Pruned-VLA recovery](pruned-vla-recovery.md) — width pruning + KD
- [BitVLA](bitvla.md) — ternary VLA
- [QuantVLA](quantvla.md) — W4A8 PTQ incl. DiT

**Rockchip RK3588**
- [RK3588 platform](rk3588-platform-specs.md) — NPU, memory, measured bandwidth
- [Rockchip toolchain](rockchip-rknn-rkllm-toolchain.md) — RKNN, RKLLM, model zoo
- [RK3588 VLM/LLM numbers](rk3588-vlm-llm-measurements.md) — tokens/s, encoders
- [RK3588 robot policies](rk3588-robot-policy-reports.md) — ACT 121 ms, SmolVLA 5 s
- [RKNN transformer reports](rknn-transformer-conversion-reports.md) — SigLIP, fusion bugs

**First-party and hardware**
- [LeRobot async docs](lerobot-async-inference-docs.md) — client/server settings
- [Gemini On-Device](gemini-robotics-on-device.md) — product, no specs
- [Helix](figure-helix.md) — 7B S2 + 80M S1
- [Jetson specs](nvidia-jetson-platform-specs.md) — Orin/Thor TOPS, GB/s
- [Sub-20-TOPS parts](edge-accelerator-datasheets.md) — Hailo, Pi HAT, Ascend
- [Unitree compute](unitree-robot-compute.md) — Go2/G1 CPU, RK3588S, Orin
- [AgiBot compute](agibot-robot-compute.md) — X2 dual RK3588, G1 Orin, G2 Thor
- [Controller reports](robot-controller-architecture-reports.md) — brain/cerebellum press release
