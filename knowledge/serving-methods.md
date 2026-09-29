---
type: concept
tags: [serving, async-inference, dual-system, device-cloud, runtime, latency-hiding]
sources: [resources/smolvla.md, resources/lerobot-async-inference-docs.md, resources/real-time-chunking.md, resources/jetson-pi.md, resources/flashvla-streaming.md, resources/vla-perf.md, resources/vla-simd.md, resources/realtime-vla.md, resources/vla-cpp.md, resources/rt-2.md, resources/openvla.md, resources/gr00t-n1.md, resources/figure-helix.md, resources/vla-xpu-characterization.md]
---
# Serving methods

## Summary
Serving a VLA means keeping a robot supplied with valid actions despite inference latency. Four families of methods stack: (1) faster execution per call (kernels, graphs, runtimes), (2) chunking with asynchronous execution so inference overlaps motion, (3) chunk-stitching or latency-aware decoding so late chunks stay consistent, and (4) placement (on-device, edge server, cloud) and dual-system splits that run only a small model at control rate. Which one matters depends on whether the latency is below or above the control period.

## Details
**1. Faster execution per call (batch size 1)**
- Graph capture, fused kernels and tuned GEMMs turned π0 from 113.9 ms to 36.8 ms on an RTX 4090; overheads dominate small-batch runs ([Realtime-VLA](../resources/realtime-vla.md), [workload note](inference-workload-characterization.md)).
- Portable runtimes: vla.cpp (llama.cpp/ggml, 11 models, CUDA/Metal/CPU/SYCL/OpenVINO) matched compiled PyTorch for most models and beat it by up to 1.84× (BitVLA); TensorRT was 1.85× faster on GR00T-N1.7 in one test ([vla.cpp](../resources/vla-cpp.md)). CPU-only engines can supply 30 actions/s for tiny policies on a Pi 5 ([vla.simd](../resources/vla-simd.md)).
- Jetson-PI's system stack (CUDA-graph reuse with padded fixed-length prompts, GPU-resident buffers, unrolled flow loop) took π0.5 on Orin from 1421 ms to 413 ms ([Jetson-PI](../resources/jetson-pi.md)).

**2. Asynchronous chunked execution**
- A client executes from an action queue and requests a new chunk when the queue drops below a fraction g of the chunk; near-duplicate observations are filtered and overlapping chunks are aggregated. SmolVLA reports about 30% faster task completion and 2× completions in fixed time, with average success 73.3% vs 78.3% for synchronous (sorting task fell 70 → 50) ([SmolVLA](../resources/smolvla.md), [LeRobot docs](../resources/lerobot-async-inference-docs.md)).
- Idle-free condition: g ≥ (E[ℓ]/Δt)/n. A complementary view: continuous supply needs d = ⌈f_c ℓ⌉ ≤ H, or 2d ≤ H if stale actions are discarded ([vla.simd](../resources/vla-simd.md)). Neither condition guarantees smoothness or task success.
- Async raises reaction time to between Δ and Δ + L action steps; long latency makes observations stale ([Jetson-PI](../resources/jetson-pi.md)).

**3. Keeping late chunks consistent**
- **Real-time chunking:** freeze actions that will run during the delay and inpaint the rest with guidance; robust to +200 ms injected latency; costs extra compute (76 → 97 ms per chunk in the paper's setup) and needs diffusion/flow heads ([RTC](../resources/real-time-chunking.md)).
- **Future-state and foresight methods:** VLASH (future robot state) is discussed but not read here; Jetson-PI predicts the future VLM state and schedules VLM vs expert calls, keeping 92–97% success at delay 9 where VLASH and RTC fall to 30–60% and 81–93% on LIBERO ([Jetson-PI](../resources/jetson-pi.md)).
- **Streaming decoding:** FlashVLA keeps several chunks at staggered noise levels and emits one per pass, giving 2.43× per-step speedup and implicit async continuity but needing fine-tuning ([FlashVLA](../resources/flashvla-streaming.md)).
- Temporal ensembling degraded π0 and made real-time chunking baselines trip protective stops at +100 ms delay ([π0](../resources/pi0.md), [RTC](../resources/real-time-chunking.md)).

**4. Placement and dual-system splits**
- RT-2's 55B model ran on a multi-TPU cloud service at 1–3 Hz, serving several robots ([RT-2](../resources/rt-2.md)); OpenVLA ships a remote inference server ([OpenVLA](../resources/openvla.md)); LeRobot's PolicyServer can be remote ([LeRobot docs](../resources/lerobot-async-inference-docs.md)).
- [VLA-Perf](../resources/vla-perf.md) (π0, roofline): Thor on-device 19 Hz; an RTX 4090 edge server reaches 10 Hz even over 4G and about 100 Hz needs datacenter GPUs plus fast networks; cloud reaches high rates only asynchronously; dual-system async gives 1.3–1.46× on Thor and only 1.05–1.06× on a B100 behind a 5G link.
- Gemini Robotics On-Device is offered as a fully local VLA with no published latency or hardware figures ([Gemini On-Device](../resources/gemini-robotics-on-device.md)).
- GR00T N1 runs its VLM at about 10 Hz and DiT at 120 Hz; Helix runs a 7B VLM at 7–9 Hz and an 80M policy at 200 Hz on embedded GPUs ([GR00T N1](../resources/gr00t-n1.md), [Helix](../resources/figure-helix.md)).
- Power argument for on-board inference: an RTX 4090 cut a robot's battery life by up to 6× relative to Jetson Orin in one estimate ([Jetson-PI](../resources/jetson-pi.md)). A cost-energy-time leaderboard found Thor best on energy for π0.5 and a 4090 best on time ([XPU](../resources/vla-xpu-characterization.md)).

**Choosing a method (inferences)**
- Latency below the control period: kernel work only. Latency between one control period and the chunk duration: async with chunk stitching. Latency above the chunk duration: shrink the model or move the heavy phase off the control loop (dual system).
- Any method that adds compute per call (RTC guidance, VLM re-invocation) must be counted in the latency it is meant to hide.

## Open questions
- Head-to-head comparison of RTC, VLASH, Jetson-PI and FlashVLA under one protocol on the same edge device is not available.
