---
type: entity
tags: [rk3588, act, smolvla, so-arm101, community, low-evidence]
sources: [https://github.com/zizhennini/RK3588-SO-ARM101, https://github.com/zizhennini/RK3588-Based-Edge-Side-Embodied-Intelligent-Actuator]
---
# RK3588 robot-policy deployments (community repositories)

## Summary
Two related GitHub projects by one author put SO-ARM101 arms on an RK3588 board. The README of one reports ACT at about 121 ms per forward pass on the NPU and SmolVLA at about 5049 ms as a three-module RKNN pipeline, and concludes SmolVLA cannot keep an action queue filled. These are the only VLA-related RK3588 numbers found, they are self-reported, and the same README lists the trained-model-on-NPU result as unverified.

## Details
- **ACT (README of RK3588-SO-ARM101):** "single forward ≈121 ms (float16, 114 MB, real measured)", producing 100 action steps; at 20–30 Hz control the NPU duty cycle is 2–4%. The control loop runs inference inline when the queue empties because 121 ms is small against about 3.3 s of action execution.
- **SmolVLA on the same board:** "three-module RKNN ≈5049 ms (real measured)", stated as 42× slower than ACT; the README says inference time exceeds action-block duration, "causing queue starvation inevitably". Module names, per-module times, precision and camera count are not given.
- **Conversion pitfalls recorded (rknn-toolkit2 2.3.2):** LayerNorm fusion crashes, worked around by disabling fusion rules (ACT always triggers it); RKNN silently reorders inputs, so with two same-shaped camera images the input order was found by brute-force permutation against ONNX Runtime; `onnx.mapping` was removed in onnx ≥ 1.17 and needed a compatibility shim; RKNN inference defaults to NHWC and `nchw` must be requested explicitly.
- **Other measured items in the README:** ResNet-18 on the NPU 8.28 ms; RealSense D435i streaming 640×480 at 30 fps; LeRobot motor, robot and camera modules installed without PyTorch (about 8 GB saved); 25 of 25 unit tests pass without a board.
- **Verification status stated by the author:** the ONNX→RKNN toolchain is validated end to end; a real trained model on the NPU and production trajectory tracking are listed as unverified. The sibling repository (edge embodied actuator) describes a lightweight Qwen-series VLM for vision-guided grasping as an experimental feature and gives no latency numbers; hardware-accelerated h264 recording keeps CPU use under 10%.
- **Trust level:** community README, single author, no task-success numbers. Treat 121 ms and 5049 ms as plausible orders of magnitude, consistent with the first-party component numbers in [RK3588 VLM/LLM measurements](rk3588-vlm-llm-measurements.md) (SmolVLM-256M's image encoder alone takes 842 ms), not as benchmarks.

See also: [Rockchip toolchain](rockchip-rknn-rkllm-toolchain.md), [RKNN transformer reports](rknn-transformer-conversion-reports.md), [SmolVLA](../models/smolvla.md).
