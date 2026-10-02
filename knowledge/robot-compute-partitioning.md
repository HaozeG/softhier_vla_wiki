---
type: concept
tags: [robot-hardware, unitree, agibot, rk3588, jetson-orin, brain-cerebellum, partitioning, rk3588-models]
sources: [resources/hardware/unitree-robot-compute.md, resources/hardware/agibot-robot-compute.md, resources/hardware/robot-controller-architecture-reports.md, resources/rk3588/rockchip-rknn-rkllm-toolchain.md, resources/rk3588/rk3588-vlm-llm-measurements.md, resources/rk3588/rk3588-robot-policy-reports.md, resources/hardware/nvidia-jetson-platform-specs.md]
---
# Robot compute partitioning: what runs where on commercial robots

## Summary
Commercial robots that publish their hardware separate the fast, deterministic joint control from heavier AI, and the split follows model size. Most published designs use a CPU-class control side (an 8-core CPU on Unitree; dual RK3588 on AgiBot's X2, though sources disagree on their role) and put large AI models on a separate NVIDIA Jetson (Orin NX, AGX Orin, or Thor), optional on Unitree's EDU models and standard on AgiBot's research and next-generation robots. Small walking policies do not need the second tier: AgiBot's open X1 runs its walking policy and its 1 kHz joint drivers in one process on one x86 controller, and Unitree's examples run the policy on a plain computer. The RK3588's 6-TOPS NPU is best evidenced for CNN vision, small language models and ACT-style policies, not for a full VLA. Marketing pages give no software map or control rates, but the vendors' open code does. Unitree has two separate examples: an SDK example that sends motor commands every 2 ms, and a walking-policy example that runs at 50 Hz. AgiBot's open X1 stack uses a 1 kHz control setting on an x86 controller. AgiBot's GO-1 manipulation model is offered as a remote policy server because robots "may not have powerful GPUs". These are example-code settings for the G1, H1, H1_2 and X1, not measurements of the shipped controllers, and they do not show which processor closes the joint loop on a Unitree robot.

```text
+--------------------------------------------------------------------------+
| AI TIER: large perception, language and VLA models, low rate             |
| Jetson Orin NX / AGX Orin / Thor,  or  a remote GPU server (GO-1 option) |
| GO-1: one chunk of 30 actions per call                                   |
+--------------------------------------------------------------------------+
                                      |
                                      |  action chunks (inferred interface),
                                      |  about one call per second in GO-1
                                      v
+--------------------------------------------------------------------------+
| CONTROL SIDE: deterministic, low latency, small policies (example rates) |
| 8-core CPU, RK3588 (<= 6 TOPS NPU), or x86 real-time controller          |
|   walking policy    50 Hz   (Unitree example, on an external computer)   |
|   motor commands    every 2 ms (Unitree G1 SDK example)                  |
|   joint drivers     up to 1 kHz                                          |
| AgiBot X1: policy and 1 kHz drivers share one process on one x86 box     |
+--------------------------------------------------------------------------+
```

## Details
**Pattern by vendor (see the source notes for the caveats)**

| Robot                | Motion / interaction side                                     | AI side                                                  | Evidence                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Unitree Go2          | RK3588S SoC per a firmware teardown; vendor says "8-core CPU" | optional Orin (40–100 TOPS) on EDU                       | teardown third-party; vendor page ([Unitree](../resources/hardware/unitree-robot-compute.md))                                                                            |
| Unitree G1 EDU       | dedicated motion-control computer, closed to users            | Jetson Orin NX 16 GB dev computer                        | documentation mirror ([Unitree](../resources/hardware/unitree-robot-compute.md))                                                                                         |
| AgiBot X2 / X2 Ultra | dual RK3588 (role reported inconsistently)                    | Orin NX on Ultra                                         | vendor page plus a secondary report ([AgiBot](../resources/hardware/agibot-robot-compute.md), [reports](../resources/hardware/robot-controller-architecture-reports.md)) |
| AgiBot G1            | not described                                                 | Jetson AGX Orin 64 GB                                    | vendor page                                                                                                                                                              |
| AgiBot G2            | not described (Thor is the "core domain controller")          | Jetson Thor, for model execution and real-time inference | vendor announcement                                                                                                                                                      |

- **Why the split exists:** the motion side needs "extremely high determinism and low-latency", while the AI side needs large memory bandwidth and matrix throughput ([reports](../resources/hardware/robot-controller-architecture-reports.md)). Chips with lockstep real-time cores and a separate NPU are marketed for this (D-Robotics S100, SemiDrive D9), so the split is a product trend, not only a Unitree or AgiBot choice. The AgiBot X1 shows the other end: with only a small policy, one real-time-kernel x86 controller does both jobs.
- **Locomotion policies are small.** Unitree's open training code exports small MLP or LSTM policies, called as a TorchScript model on a plain CPU (a LibTorch C++ path also exists); these need no NPU ([Unitree](../resources/hardware/unitree-robot-compute.md)). The compute-hungry workloads are perception (LiDAR, cameras) and language or VLA models, which is where the Jetson tier appears.
- **Tier by compute:** a built-in 8-core CPU or RK3588 (up to 6 TOPS NPU) for control and light perception; Orin NX 16 GB and AGX Orin 64 GB for the AI computer (NVIDIA lists 157 and up to 275 sparse INT8 TOPS, see [Jetson specs](../resources/hardware/nvidia-jetson-platform-specs.md); Unitree's older material quotes 100 TOPS for the Orin NX, a dense/sparse difference that is unresolved here); Thor (AgiBot G2) as the newest tier. This lines up with the device classes in [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md): the ~10-TOPS class is the controller tier, not the AI tier, for these robots.

**Where software runs and at what rate (open code; example settings, not measured production loops)**

| Layer                                | Placement                                                                                                                  | Rate                                                                                                                                      | Source                                                    |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Built-in motion program (G1)         | motion-control computer; must be released ("debug mode" or motion-switcher release) before user code can command motors    | not published                                                                                                                             | [Unitree](../resources/hardware/unitree-robot-compute.md) |
| User motor commands (G1 SDK example) | message bus (DDS) topics `rt/lowcmd` / `rt/lowstate`, from a host computer or PC2; gains ride on each command              | 2 ms period, state about 500 Hz                                                                                                           | Unitree SDK example                                       |
| Walking policy (Unitree example)     | TorchScript on an external computer over Ethernet                                                                          | 50 Hz (`control_dt` 0.02)                                                                                                                 | `unitree_rl_gym`                                          |
| Teleoperation, cameras, hands (G1)   | host PC runs teleoperation; PC2 runs image and hand services                                                               | teleoperation default 30 Hz                                                                                                               | `xr_teleoperate`                                          |
| Walking policy (AgiBot X1)           | ONNX in the RL control module, in the same process as the joint driver, on the x86 main controller with a real-time kernel | controller `freq` 1000; joint, IMU and command topics 1 kHz                                                                               | [AgiBot](../resources/hardware/agibot-robot-compute.md)   |
| Joint drivers (X1)                   | domain control units over EtherCAT, three CAN-FD buses each                                                                | up to 1 kHz                                                                                                                               | same                                                      |
| Manipulation model GO-1              | about 7 GB GPU (RTX 4090 example); remote policy server offered                                                            | chunk of 30 actions played at 30 Hz, so about one model call per second (the 30 Hz is a data and playback setting, not an inference rate) | Agibot-World repository and report                        |

- **Pattern:** joint-level loops run at 500 Hz to 1 kHz, walking policies at 50 Hz (Unitree example) or inside a 1 kHz loop with a sampling-interval setting (AgiBot X1), and the large manipulation model is either on a GPU-class module or off the robot. Small policies share the control computer (X1); large models do not. The two-rate structure matches the VLA serving designs in [serving methods](serving-methods.md).
- **A limit of this evidence:** these repositories cover the G1, H1, H1_2 and X1. They say nothing about the Go2's or the X2's loops, and the X1's x86 controller is not the X2's dual RK3588.

**What runs on the RK3588 NPU (from the RK3588 notes)**
- Vision CNNs from Rockchip's model zoo at INT8: YOLOv5–v11 (YOLOv8n 73.5 FPS on one core, 199 FPS on three), MobileNet and ResNet classifiers, segmentation (DeepLabv3, MobileSAM), pose, OCR, CLIP. Speech models (Whisper, Wav2Vec2) at FP16 ([toolchain](../resources/rk3588/rockchip-rknn-rkllm-toolchain.md)).
- Language and vision-language models through RKLLM at W8A8: Qwen2/2.5/3, Llama-family, Gemma, ChatGLM3, plus VLMs such as Qwen2-VL, MiniCPM-V, InternVL2/3-1B and SmolVLM; decode from 78 tokens/s (SmolVLM-256M) to 5 tokens/s (6B), with the vision encoder in FP16 and taking 0.8–3.3 s per image in the published rows ([measurements](../resources/rk3588/rk3588-vlm-llm-measurements.md)).
- Robot policies: an ACT-style policy at about 121 ms per chunk (self-reported); SmolVLA at about 5 s per chunk ([policy reports](../resources/rk3588/rk3588-robot-policy-reports.md), details in [RK3588 deployment](rk3588-vla-deployment.md)).

**Evidence quality:** vendor product pages are marketing-level and omit software, while the open repositories (first-party code and docs) give rates and placement for specific robots; the Go2's RK3588S identification and the G1 EDU two-computer layout are third-party; the AgiBot X2 role assignment is contradictory between sources; the market summary is a press release. Nothing here is a measured latency of a VLA on a commercial robot.

## Open questions
- Which board runs the motion controller on the Go2, and at what rate; whether AgiBot's X2 runs any perception on its RK3588 NPUs; the built-in controller loop rate on either company's shipped robots.
- Whether Thor-based robots run a VLA in the control loop or as a slow planner; where GO-1 runs on an AgiBot G1 (onboard AGX Orin or a server) and at what latency.
- The Orin NX TOPS discrepancy (100 versus 157) as it applies to the robots' actual power mode.
