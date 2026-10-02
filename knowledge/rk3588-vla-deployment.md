---
type: concept
tags: [rk3588, rockchip, npu, deployment, smolvla, act, practices]
sources: [resources/rk3588/rk3588-platform-specs.md, resources/rk3588/rockchip-rknn-rkllm-toolchain.md, resources/rk3588/rk3588-vlm-llm-measurements.md, resources/rk3588/rk3588-robot-policy-reports.md, resources/rk3588/rknn-transformer-conversion-reports.md, resources/serving/embodied-cpp.md, resources/surveys/survey-embodied-fm-edge.md, resources/serving/vla-simd.md, resources/models/smolvla.md]
---
# RK3588 deployment: practices and evidence for VLAs

## Summary
On the RK3588's 6-TOPS NPU the sources report CNN vision, LLM and VLM decoding (5–78 tokens/s, W8A8 only) and small ACT-style policies (about 0.12 s per chunk, self-reported). A SmolVLA-class VLA has one community measurement, about 5 s per 50-action chunk, which the README says exceeds the action-block duration so that the queue starves. The toolchain is the main constraint reported: transformers convert fragilely, only W8A8 is available for the language model, and the vision encoder runs in FP16 through a separate toolchain. Reported practice on these boards includes hardware video paths and running ACT-style policies inline at the control rate.

The picture shows how the toolchain note says a VLA has to be divided (SmolVLA's sizes from its paper); the one SmolVLA port reported used three RKNN modules.

```text
A VLA SPLIT ACROSS THE RK3588 TOOLCHAINS (the toolchain note)
camera frames, 1 to 3
  |
  v
+--------------------------------------+
| vision encoder: RKNN, FP16           |
+--------------------------------------+
  |
  v 64 visual tokens per camera
+--------------------------------------+
| language model: RKLLM, W8A8          |
+--------------------------------------+
  |
  v keys + values of the prefix
+--------------------------------------+
| action expert, 10 flow steps:        |---+
| RKNN graph or CPU; RKLLM             |   | x10: velocity of
| cannot convert it                    |<--+ 50 action tokens
+--------------------------------------+
  |
  v chunk of 50 actions
```

## Details
**What runs on RK3588 today (evidence and trust)**

| Workload                      | Reported result                                                             | Source and trust                                                                                                                                                          |
| ----------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| YOLOv8n INT8, 640×640         | 73.5 FPS single core; 199 FPS with three cores; INT8 costs 0.5–1.5 mAP      | [Rockchip model zoo](../resources/rk3588/rockchip-rknn-rkllm-toolchain.md) first-party; [community benchmark](../resources/rk3588/rknn-transformer-conversion-reports.md) |
| ACT policy, FP16, 114 MB      | about 121 ms per forward pass, 100 actions; 2–4% NPU duty cycle at 20–30 Hz | [community README](../resources/rk3588/rk3588-robot-policy-reports.md); trained model on NPU listed unverified                                                            |
| SmolVLA as three RKNN modules | about 5049 ms per chunk, "queue starvation inevitably"                      | same README; per-module times and camera count not given                                                                                                                  |
| LLM decode, W8A8              | Qwen2 0.5B 41.6 tok/s; Qwen2.5 1.5B 16.7; ChatGLM3 6B 5.0                   | [Rockchip RKLLM benchmark](../resources/rk3588/rk3588-vlm-llm-measurements.md) first-party                                                                                |
| VLM SmolVLM-256M              | image encoder 842 ms at 512×512, prefill 77 ms, decode 78 tok/s             | same table, first-party                                                                                                                                                   |
| VLM Qwen2-VL-2B               | encoder 3.28 s at 392×392, prefill 633 ms, decode 16.6 tok/s                | same table                                                                                                                                                                |

**Practices that recur across the sources**
- **Split the model by toolchain.** Vision encoder through RKNN (FP16 in every published VLM port); language model through RKLLM at W8A8; RKLLM does not convert action heads, cross-attention experts or flow loops, so a VLA's expert must be an RKNN graph or run on CPU ([toolchain](../resources/rk3588/rockchip-rknn-rkllm-toolchain.md)).
- **Validate every conversion against ONNX Runtime.** LayerNorm fusion crashes, silently reordered inputs for same-shaped camera images, NHWC defaults, and fused attention producing wrong outputs at FP16 were all reported ([robot-policy reports](../resources/rk3588/rk3588-robot-policy-reports.md), [transformer reports](../resources/rk3588/rknn-transformer-conversion-reports.md)). Pin toolkit, runtime library and driver versions; an RKLLM model must match its runtime.
- **Treat SigLIP-class encoders carefully.** One engineer needed manual tiling, 26 shards across the three NPU cores and input rescaling to make a SigLIP run in INT8 within accuracy; Rockchip's own ports keep the encoder in FP16 ([transformer reports](../resources/rk3588/rknn-transformer-conversion-reports.md)).
- **Use the hardware media path.** MPP decode, RGA resize and zero-copy input kept CPU use under 10% while recording and gave the 640×640 YOLO numbers; software resizing would compete with the policy for the same DRAM ([robot-policy reports](../resources/rk3588/rk3588-robot-policy-reports.md), [community benchmark](../resources/rk3588/rknn-transformer-conversion-reports.md)).
- **What the policy READMEs report.** The ACT-style policy runs inference inline when the action queue empties, with no threads needed; the SmolVLA port's README says its inference time exceeds the action-block duration, causing queue starvation ([robot-policy reports](../resources/rk3588/rk3588-robot-policy-reports.md)).
- **Watch shared DRAM and heat.** Concurrent sessions each dropped to 40–65% of single-session throughput; CPU, GPU, NPU and sensors share LPDDR, and mixed-load throttling was reported to cut throughput by up to 60% in cited work ([platform](../resources/rk3588/rk3588-platform-specs.md), [edge survey](../resources/surveys/survey-embodied-fm-edge.md)).
- **Budget model size.** About 2–3 GB of models is the practical range on 8–16 GB boards; the Qwen3-VL-2B port used 3.1 GB ([measurements](../resources/rk3588/rk3588-vlm-llm-measurements.md)).

**Evidence quality:** Rockchip's numbers are first-party and reproducible; every VLA-specific number here is a single community README. No source reports task success for a policy running on the RK3588 NPU. [Embodied.cpp](../resources/serving/embodied-cpp.md) names RK boards as a target but reports none.

## Open questions
- Per-module SmolVLA timings and camera count behind the 5049 ms figure; whether RKNN supports cross-attention with cached K/V and a 10-step loop without CPU fallback.
- Task success of INT8 and FP16 converted policies on real hardware.
- Behavior under thermal load and with camera, encoder and NPU sharing DRAM.
- Whether the three NPU cores can be scheduled to split one image's encoder (as the shard experiment did) without a custom runtime.

See also: [robot compute partitioning](robot-compute-partitioning.md) for how commercial robots use the RK3588 alongside Jetson modules.
