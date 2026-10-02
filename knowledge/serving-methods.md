---
type: concept
tags: [serving, async-inference, dual-system, device-cloud, runtime, latency-hiding]
sources: [resources/models/smolvla.md, resources/serving/lerobot-async-inference-docs.md, resources/serving/real-time-chunking.md, resources/serving/jetson-pi.md, resources/serving/flashvla-streaming.md, resources/serving/vla-perf.md, resources/serving/vla-simd.md, resources/serving/realtime-vla.md, resources/serving/vla-cpp.md, resources/models/rt-2.md, resources/models/openvla.md, resources/models/gr00t-n1.md, resources/models/figure-helix.md, resources/serving/vla-xpu-characterization.md]
---
# Serving methods

## Summary
(Short forms of the terms in this note are in the glossary ([robot and control loop](../glossary/robot-and-control-loop.md), [symbols](../glossary/symbols-and-conventions.md)); the full meanings are given under "Terms used here" below.)

Serving a VLA means keeping a robot supplied with valid actions despite inference latency. Four families of methods stack: (1) faster execution per call (kernels, graphs, runtimes), (2) chunking with asynchronous execution so inference overlaps motion, (3) chunk-stitching or latency-aware decoding so late chunks stay consistent, and (4) placement (on-device, edge server, cloud) and dual-system splits that run only a small model at control rate. The sources relate the latency of one model call to two times: the control period and the chunk duration (actions per chunk times control period).

## Diagram
```text
ASYNC CHUNKED EXECUTION (families 2 and 3; 1 and 4 act on the model call)

+------------------------------------------------------------------------+
| ROBOT CLIENT: queue of actions, pops one every dt (control period)     |
|                                                                        |
+------------------------------------------------------------------------+
          |                                         ^
          |  observation, sent when the queue holds |  new chunk: n actions;
          |  fewer than g * n actions               |  late ones stitched (3)
          v                                         |
+------------------------------------------------------------------------+
| MODEL CALL: latency l  (family 1 shrinks it, family 4 moves it)        |
|                                                                        |
+------------------------------------------------------------------------+

The request repeats whenever the queue runs low; actions keep popping meanwhile.
```

```text
Action-supply conditions of vla.simd, by latency l of one call
(n = actions per chunk, dt = control period, n*dt = chunk duration)

 0                        n*dt/2                       n*dt
 |--------------------------|----------------------------|------------> l
 |<--- 2d <= H holds ------>|
 |<------------------ d <= H holds ------------------->|
                                                             beyond: neither
 2d <= H: supply is continuous even if stale actions are discarded
 d <= H : supply is continuous if late actions are kept (lagged execution)
 (d = latency in control steps, rounded up; H = n = actions per chunk)
```
The first drawing is family 2 and where the others act; the second shows the two action-supply conditions of [vla.simd](../resources/serving/vla-simd.md) quoted under family 2.

## Details
**Terms used here**
- **Control step, control period (dt) and control rate:** a control step is one tick at which the robot sends one command (an action); the control period dt is the time between ticks; the control rate is 1/dt, for example 30 Hz ([vla.simd](../resources/serving/vla-simd.md), where the controller rate is f_c).
- **Latency (l):** the time of one model call, from the observation going in to the chunk coming out; it is not the time to finish a task ([vla.simd](../resources/serving/vla-simd.md), where it is the query latency T_q). E[l] is the expected (mean) latency, and d = ⌈f_c·l⌉ is the latency counted in control steps, rounded up, with f_c the control rate.
- **Chunk duration:** the number of actions in a chunk times dt, the time one chunk keeps the robot supplied.
- **Stale actions:** actions in a chunk that describe moments already passed, because the call took time while the robot kept moving; the first ones of a late chunk are stale. **Discarding stale actions** is "time-aligned" execution; **lagged execution** executes the late chunk from its start anyway ([vla.simd](../resources/serving/vla-simd.md), conditions C1 and C2 below).
- **Batch size:** how many inputs one pass processes together; batch size 1 means one observation per pass, which is the usual case for one robot.

**1. Faster execution per call (batch size 1)**
- Graph capture, fused kernels and tuned GEMMs turned π0 from 113.9 ms to 36.8 ms on an RTX 4090; overheads dominate small-batch runs ([Realtime-VLA](../resources/serving/realtime-vla.md), [workload note](inference-workload-characterization.md)).
- Portable runtimes: vla.cpp (llama.cpp/ggml, 11 models, CUDA/Metal/CPU/SYCL/OpenVINO) matched compiled PyTorch for most models and beat it by up to 1.84× (BitVLA); TensorRT was 1.85× faster on GR00T-N1.7 in one test ([vla.cpp](../resources/serving/vla-cpp.md)). CPU-only engines can supply 30 actions/s for tiny policies on a Pi 5 ([vla.simd](../resources/serving/vla-simd.md)).
- Jetson-PI's system stack (CUDA-graph reuse with padded fixed-length prompts, GPU-resident buffers, unrolled flow loop) took π0.5 on Orin from 1421 ms to 413 ms ([Jetson-PI](../resources/serving/jetson-pi.md)).

**2. Asynchronous chunked execution**
- A client executes from an action queue and requests a new chunk when the queue drops below a fraction g of the chunk; near-duplicate observations are filtered and overlapping chunks are aggregated. SmolVLA reports about 30% faster task completion and 2× completions in fixed time, with average success 73.3% vs 78.3% for synchronous (sorting task fell 70 → 50) ([SmolVLA](../resources/models/smolvla.md), [LeRobot docs](../resources/serving/lerobot-async-inference-docs.md)).
- Idle-free condition: g ≥ (E[ℓ]/Δt)/n, with ℓ the call latency, Δt the control period and n the chunk length. A complementary view: continuous supply needs d = ⌈f_c ℓ⌉ ≤ H, or 2d ≤ H if stale actions are discarded ([vla.simd](../resources/serving/vla-simd.md)). Neither condition guarantees smoothness or task success.
- Async makes the reaction time (delay between a change in the scene and the robot's response) fall between Δ and Δ + L action steps, where Δ is the inference latency in action steps and L the number of actions executed per chunk (L = H − Δ for chunk size H in the paper's LIBERO setup); long latency makes observations stale ([Jetson-PI](../resources/serving/jetson-pi.md)).

**3. Keeping late chunks consistent**
- **Real-time chunking:** freeze actions that will run during the delay and inpaint the rest with guidance; robust to +200 ms injected latency; costs extra compute (76 → 97 ms per chunk in the paper's setup) and needs diffusion/flow heads ([RTC](../resources/serving/real-time-chunking.md)).
- **Future-state and foresight methods:** VLASH (future robot state) is discussed but not read here; Jetson-PI predicts the future VLM state and schedules VLM vs expert calls, keeping 92–97% success at delay 9 where VLASH and RTC fall to 30–60% and 81–93% on LIBERO ([Jetson-PI](../resources/serving/jetson-pi.md)).
- **Streaming decoding:** FlashVLA keeps several chunks at staggered noise levels and emits one per pass, giving 2.43× per-step speedup and implicit async continuity but needing fine-tuning ([FlashVLA](../resources/serving/flashvla-streaming.md)).
- Temporal ensembling (averaging overlapping chunks into one action sequence) degraded π0 and made real-time chunking baselines trip protective stops at +100 ms delay ([π0](../resources/models/pi0.md), [RTC](../resources/serving/real-time-chunking.md)).

**4. Placement and dual-system splits**
- RT-2's 55B model ran on a multi-TPU cloud service at 1–3 Hz, serving several robots ([RT-2](../resources/models/rt-2.md)); OpenVLA ships a remote inference server ([OpenVLA](../resources/models/openvla.md)); LeRobot's PolicyServer can be remote ([LeRobot docs](../resources/serving/lerobot-async-inference-docs.md)).
- [VLA-Perf](../resources/serving/vla-perf.md) (π0, roofline): Thor on-device 19 Hz; an RTX 4090 edge server reaches 10 Hz even over 4G and about 100 Hz needs datacenter GPUs plus fast networks; cloud reaches high rates only asynchronously; dual-system async gives 1.3–1.46× on Thor and only 1.05–1.06× on a B100 behind a 5G link.
- Gemini Robotics On-Device is offered as a fully local VLA with no published latency or hardware figures ([Gemini On-Device](../resources/models/gemini-robotics-on-device.md)).
- GR00T N1 runs its VLM at about 10 Hz and DiT at 120 Hz; Helix runs a 7B VLM at 7–9 Hz and an 80M policy at 200 Hz on embedded GPUs ([GR00T N1](../resources/models/gr00t-n1.md), [Helix](../resources/models/figure-helix.md)).
- Power argument for on-board inference: an RTX 4090 cut a robot's battery life by up to 6× relative to Jetson Orin in one estimate ([Jetson-PI](../resources/serving/jetson-pi.md)). A cost-energy-time leaderboard found Thor best on energy for π0.5 and a 4090 best on time ([XPU](../resources/serving/vla-xpu-characterization.md)).

## Open questions
- Head-to-head comparison of RTC, VLASH, Jetson-PI and FlashVLA under one protocol on the same edge device is not available.
