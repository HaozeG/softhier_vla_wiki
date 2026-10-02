---
type: concept
tags: [serving, async-inference, dual-system, device-cloud, runtime, latency-hiding]
sources: [resources/models/smolvla.md, resources/serving/lerobot-async-inference-docs.md, resources/serving/real-time-chunking.md, resources/serving/jetson-pi.md, resources/serving/flashvla-streaming.md, resources/serving/vla-perf.md, resources/serving/vla-simd.md, resources/serving/realtime-vla.md, resources/serving/vla-cpp.md, resources/models/rt-2.md, resources/models/openvla.md, resources/models/gr00t-n1.md, resources/models/figure-helix.md, resources/serving/vla-xpu-characterization.md, resources/hardware/agibot-robot-compute.md, resources/models/pi0.md, resources/models/gemini-robotics-on-device.md]
---
# Serving methods

## Summary
(Terms: [robot and control loop](../glossary/robot-and-control-loop.md), [symbols](../glossary/symbols-and-conventions.md).)

Serving a VLA means keeping a robot supplied with valid actions despite inference latency. Four families of methods stack: (1) faster execution per call (kernels, graphs, runtimes), (2) chunking with asynchronous execution so inference overlaps motion, (3) chunk-stitching or latency-aware decoding so late chunks stay consistent, and (4) placement (on-device, edge server, cloud) and dual-system splits that run only a small model at control rate. The sources relate the latency of one model call to two times: the control period and the chunk duration (actions per chunk times control period).

## Diagram
```text
ASYNC EXECUTION OVER TIME (LeRobot async docs, SmolVLA paper)

queue n  |  *****                              *****
         |       *****                              *****
         |            *****                              *****
g*n      |                 *****                              *****
         |                      *****                              *****
         |                           *****                              *****
1        |                                *****                              *
         |
         +------------------------------------------------------------> time
                           R                   C                R
model call                 [ call 1: latency l ]                [ call 2 ...
robot       pops one action each dt and keeps moving during calls

R: queue falls to g*n; observation (images, text, state) goes to the model.
C: chunk of n actions comes back while some of chunk 1 is still queued;
   overlapping actions are aggregated, the queue is refilled to about n.
```

```text
Action-supply conditions of vla.simd, by latency l of one call
(n = actions per chunk, dt = control period, n*dt = chunk duration)

 0                        n*dt/2                       n*dt
 |--------------------------|----------------------------|------------> l
 |<--- 2d <= n holds ------>|
 |<------------------ d <= n holds --------------------->|
                                                             beyond: neither
 2d <= n: supply is continuous even if stale actions are discarded
 d <= n : supply is continuous if late actions are kept (lagged execution)
 (d = latency in control steps, rounded up; n = actions per chunk)
```
The first drawing is families 2 and 3 over time; the second shows the two action-supply conditions of [vla.simd](../resources/serving/vla-simd.md) quoted under family 2. The table after the notation lists what the sources report for each latency range.

## Details
**Notation used in this note** (one letter per meaning; definitions in the [glossary](../glossary/robot-and-control-loop.md))
- l is the latency of one call (a time) and dt the control period. d is the latency counted in control steps, rounded up (Δ in Jetson-PI). n and H are the same quantity, the number of actions in a chunk. s is the number of actions executed from a chunk before the next one is used (L in Jetson-PI, the execution horizon in RTC). g is the fraction of a chunk left in the queue at which the next call is requested. E[l] is the expected latency.
- Stale actions are the early actions of a late chunk that describe moments already passed. In [vla.simd](../resources/serving/vla-simd.md) the condition d ≤ n (C1) holds for lagged execution, which keeps the late actions, and 2d ≤ n (C2) holds for time-aligned execution, which discards the stale ones.

**Latency against control period and chunk duration: what the sources report**

| Latency l         | Conditions that hold ([vla.simd](../resources/serving/vla-simd.md))                | What the sources report for delays in this range                                                                                                                                                                                                                                      | Not reported                                  |
| ----------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| below dt          | d is one control step, so both C1 and C2 hold for any chunk of two or more actions | Faster execution per call (family 1) reports latencies for single models, for example π0 on an RTX 4090 ([Realtime-VLA](../resources/serving/realtime-vla.md))                                                                                                                        | A method named for this range                 |
| dt up to n·dt/2   | C1 and C2 hold: supply is continuous even if stale actions are discarded           | Real-time chunking with delays of about six control steps (LAN) up to about sixteen (injected) for n = 50 ([RTC](../resources/serving/real-time-chunking.md)); Jetson-PI at a delay of nine steps with n = 20, against VLASH and RTC ([Jetson-PI](../resources/serving/jetson-pi.md)) | Task success when stale actions are discarded |
| n·dt/2 up to n·dt | only C1 holds: supply is continuous only if late actions are kept (lagged)         | RTC's formulation requires d ≤ s ≤ n − d, which limits d to half of n ([RTC](../resources/serving/real-time-chunking.md))                                                                                                                                                             | A method tested in this range                 |
| above n·dt        | neither holds: the queue runs empty                                                | Dual-system splits run a large model slowly beside a fast policy ([GR00T N1](../resources/models/gr00t-n1.md), [Helix](../resources/models/figure-helix.md), [VLA-Perf](../resources/serving/vla-perf.md))                                                                            | A source that ties a method to this range     |

**1. Faster execution per call (batch size 1)**
- Graph capture, fused kernels and tuned GEMMs turned π0 from 113.9 ms to 36.8 ms on an RTX 4090; overheads dominate small-batch runs ([Realtime-VLA](../resources/serving/realtime-vla.md), [workload note](inference-workload-characterization.md)).
- Portable runtimes: vla.cpp (llama.cpp/ggml, 11 models, CUDA/Metal/CPU/SYCL/OpenVINO) matched compiled PyTorch for most models and beat it by up to 1.84× (BitVLA); TensorRT was 1.85× faster on GR00T-N1.7 in one test ([vla.cpp](../resources/serving/vla-cpp.md)). CPU-only engines can supply 30 actions/s for tiny policies on a Pi 5 ([vla.simd](../resources/serving/vla-simd.md)).
- Jetson-PI's system stack (CUDA-graph reuse with padded fixed-length prompts, GPU-resident buffers, unrolled flow loop) took π0.5 on Orin from 1421 ms to 413 ms ([Jetson-PI](../resources/serving/jetson-pi.md)).

**2. Asynchronous chunked execution**
- A client executes from an action queue and requests a new chunk when the queue drops below a fraction g of the chunk; near-duplicate observations are filtered and overlapping chunks are aggregated. SmolVLA reports about 30% faster task completion and 2× completions in fixed time, with average success 73.3% vs 78.3% for synchronous (sorting task fell 70 → 50) ([SmolVLA](../resources/models/smolvla.md), [LeRobot docs](../resources/serving/lerobot-async-inference-docs.md)).
- Idle-free condition: g ≥ (E[l]/dt)/n ([SmolVLA](../resources/models/smolvla.md)). A complementary view: continuous supply needs d = ⌈f_c·l⌉ ≤ n, or 2d ≤ n if stale actions are discarded, with f_c the control rate ([vla.simd](../resources/serving/vla-simd.md)). Neither condition guarantees smoothness or task success.
- Async makes the reaction time (delay between a change in the scene and the robot's response) fall between d and d + s action steps (Δ and L in the paper), where s = n − d in the paper's LIBERO setup; long latency makes observations stale ([Jetson-PI](../resources/serving/jetson-pi.md)).

**3. Keeping late chunks consistent**
- **Real-time chunking:** freeze actions that will run during the delay and inpaint the rest with guidance; robust to +200 ms injected latency; costs extra compute (76 → 97 ms per chunk in the paper's setup) and needs diffusion/flow heads ([RTC](../resources/serving/real-time-chunking.md)).
- **Future-state and foresight methods:** VLASH (future robot state) is discussed but not read here; Jetson-PI predicts the future VLM state and schedules VLM vs expert calls, keeping 92–97% success at delay 9 where VLASH and RTC fall to 30–60% and 81–93% on LIBERO ([Jetson-PI](../resources/serving/jetson-pi.md)).
- **Streaming decoding:** FlashVLA keeps several chunks at staggered noise levels and emits one per pass, giving 2.43× per-step speedup and implicit async continuity but needing fine-tuning ([FlashVLA](../resources/serving/flashvla-streaming.md)).
- Temporal ensembling (averaging overlapping chunks into one action sequence) degraded π0 and made real-time chunking baselines trip protective stops at +100 ms delay ([π0](../resources/models/pi0.md), [RTC](../resources/serving/real-time-chunking.md)).

**4. Placements the sources report**

| Placement                | Reported result                                                                                                                        | Source                                                                                                                        | Caveat                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| On the robot             | π0: 73 ms per call on an on-board RTX 4090; roofline of 19 Hz on Jetson Thor                                                           | [π0](../resources/models/pi0.md); [VLA-Perf](../resources/serving/vla-perf.md)                                                | VLA-Perf is an optimistic upper-bound model                                   |
| On the robot, two speeds | Helix: 7B vision-language model at 7–9 Hz plus an 80M policy at 200 Hz on embedded GPUs; GR00T N1: model at about 10 Hz, DiT at 120 Hz | [Helix](../resources/models/figure-helix.md); [GR00T N1](../resources/models/gr00t-n1.md)                                     | Helix is a company page with rates and sizes only                             |
| On the robot, no figures | Gemini Robotics On-Device runs fully locally                                                                                           | [Gemini On-Device](../resources/models/gemini-robotics-on-device.md)                                                          | No latency or hardware reported                                               |
| Edge server              | An RTX 4090 server reaches 10 Hz for π0 even over 4G; about 100 Hz needs datacenter GPUs and fast networks                             | [VLA-Perf](../resources/serving/vla-perf.md)                                                                                  | Roofline model; π0 off-board is 86 ms including 13 ms network in the π0 paper |
| Policy server            | LeRobot's PolicyServer may run on another machine; the GO-1 repository ships a policy server and names an RTX 4090 as example GPU      | [LeRobot docs](../resources/serving/lerobot-async-inference-docs.md); [AgiBot](../resources/hardware/agibot-robot-compute.md) | Where GO-1 runs on a G1 or G2 and its latency are not reported                |
| Cloud                    | RT-2's 55B model ran on a multi-TPU cloud service at 1–3 Hz for several robots; high rates only with async inference                   | [RT-2](../resources/models/rt-2.md); [VLA-Perf](../resources/serving/vla-perf.md)                                             | VLA-Perf is a model, not a measurement                                        |
| Dual system, async       | 1.3–1.46× on Thor and 1.05–1.06× on a B100 behind a 5G link                                                                            | [VLA-Perf](../resources/serving/vla-perf.md)                                                                                  | Roofline model                                                                |

- Energy: an RTX 4090 cut a robot's battery life by up to 6× relative to Jetson Orin in one estimate by the source ([Jetson-PI](../resources/serving/jetson-pi.md)); a cost-energy-time leaderboard found Thor best on energy for π0.5 and a 4090 best on time ([XPU](../resources/serving/vla-xpu-characterization.md)). OpenVLA ships a remote inference server ([OpenVLA](../resources/models/openvla.md)).

## Open questions
- Head-to-head comparison of RTC, VLASH, Jetson-PI and FlashVLA under one protocol on the same edge device is not available.
