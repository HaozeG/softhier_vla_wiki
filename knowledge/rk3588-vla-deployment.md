---
type: concept
tags: [rk3588, rockchip, npu, deployment, smolvla, act, practices, estimate]
sources: [resources/rk3588-platform-specs.md, resources/rockchip-rknn-rkllm-toolchain.md, resources/rk3588-vlm-llm-measurements.md, resources/rk3588-robot-policy-reports.md, resources/rknn-transformer-conversion-reports.md, resources/embodied-cpp.md, resources/survey-embodied-fm-edge.md, resources/vla-simd.md, resources/smolvla.md]
---
# RK3588 deployment: practices and evidence for VLAs

## Summary
On the RK3588's 6-TOPS NPU, what is well evidenced is CNN vision, LLM and VLM decoding (5–60 tokens/s, W8A8 only) and small ACT-style policies (about 0.12 s per chunk, self-reported). A SmolVLA-class VLA has one community measurement, about 5 s per 50-action chunk, and component data from Rockchip implies about 1–1.4 s with one camera and about 2.8–3.2 s with three, so it cannot keep a 30 Hz robot supplied with 50-action chunks (a chunk lasts 1.67 s). The NPU is used at about 4–19% of its headline TOPS in the measured transformer workloads, and the toolchain is the main risk: transformers convert fragilely, only W8A8 is available for the language model, and the vision encoder runs in FP16 through a separate toolchain. Practice on these boards is therefore ACT-class policies at control rate, VLMs off the control loop, and hardware video paths.

## Details
**What runs on RK3588 today (evidence and trust)**

| Workload | Reported result | Source and trust |
|---|---|---|
| YOLOv8n INT8, 640×640 | 73.5 FPS single core; 199 FPS with three cores; INT8 costs 0.5–1.5 mAP | [Rockchip model zoo](../resources/rockchip-rknn-rkllm-toolchain.md) first-party; [community benchmark](../resources/rknn-transformer-conversion-reports.md) |
| ACT policy, FP16, 114 MB | about 121 ms per forward pass, 100 actions; 2–4% NPU duty cycle at 20–30 Hz | [community README](../resources/rk3588-robot-policy-reports.md); trained model on NPU listed unverified |
| SmolVLA as three RKNN modules | about 5049 ms per chunk, "queue starvation inevitably" | same README; per-module times and camera count not given |
| LLM decode, W8A8 | Qwen2 0.5B 41.6 tok/s; Qwen2.5 1.5B 16.7; ChatGLM3 6B 5.0 | [Rockchip RKLLM benchmark](../resources/rk3588-vlm-llm-measurements.md) first-party |
| VLM SmolVLM-256M | image encoder 842 ms at 512×512, prefill 77 ms, decode 78 tok/s | same table, first-party |
| VLM Qwen2-VL-2B | encoder 3.28 s at 392×392, prefill 633 ms, decode 16.6 tok/s | same table |

**Practices that recur across the sources**
- **Split the model by toolchain.** Vision encoder through RKNN (FP16 in every published VLM port); language model through RKLLM at W8A8; RKLLM does not convert action heads, cross-attention experts or flow loops, so a VLA's expert must be an RKNN graph or run on CPU ([toolchain](../resources/rockchip-rknn-rkllm-toolchain.md)).
- **Validate every conversion against ONNX Runtime.** LayerNorm fusion crashes, silently reordered inputs for same-shaped camera images, NHWC defaults, and fused attention producing wrong outputs at FP16 were all reported ([robot-policy reports](../resources/rk3588-robot-policy-reports.md), [transformer reports](../resources/rknn-transformer-conversion-reports.md)). Pin toolkit, runtime library and driver versions; an RKLLM model must match its runtime.
- **Treat SigLIP-class encoders carefully.** One engineer needed manual tiling, 26 shards across the three NPU cores and input rescaling to make a SigLIP run in INT8 within accuracy; Rockchip's own ports keep the encoder in FP16 ([transformer reports](../resources/rknn-transformer-conversion-reports.md)).
- **Use the hardware media path.** MPP decode, RGA resize and zero-copy input kept CPU use under 10% while recording and gave the 640×640 YOLO numbers; software resizing would compete with the policy for the same DRAM ([robot-policy reports](../resources/rk3588-robot-policy-reports.md), [community benchmark](../resources/rknn-transformer-conversion-reports.md)).
- **Match policy class to latency.** ACT-style single-pass policies fit (inference inline when the action queue empties, no threads needed); autoregressive or multi-stage VLAs need a dual-system split with the slow model off the control loop ([serving methods](serving-methods.md)).
- **Watch shared DRAM and heat.** Concurrent sessions each dropped to 40–65% of single-session throughput; CPU, GPU, NPU and sensors share LPDDR, and mixed-load throttling was reported to cut throughput by up to 60% in cited work ([platform](../resources/rk3588-platform-specs.md), [edge survey](../resources/survey-embodied-fm-edge.md)).
- **Budget model size.** About 2–3 GB of models is the practical range on 8–16 GB boards; the Qwen3-VL-2B port used 3.1 GB ([measurements](../resources/rk3588-vlm-llm-measurements.md)).

**Utilization of the 6 TOPS (derived from Rockchip's tables; parameter counts are nominal)**
- Decode: weight traffic implied by memory × tokens/s is 24–30 GB/s across nine models, i.e. memory-bound near practical DRAM bandwidth.
- Prefill: 0.73–1.15 TFLOP/s effective, 12–19% of 6 TOPS. Vision encoder (SmolVLM-256M at 512×512): about 0.25 TFLOP/s, about 4%. These are the numbers to use instead of the headline when sizing a model ([edge budget estimate](edge-budget-estimate.md) uses the headline as a roofline).

**Estimate for a SmolVLA-class call on RK3588 (derived; not a measurement)**
- Inputs: vision per camera about 0.84 s (SmolVLM-256M as proxy; the tower dimensions match SmolVLA's, depth may differ); LLM prefix scaled from the 77 ms / 128-token row by parameters (157M vs about 106M non-embedding) and tokens (113–241) gives 0.10–0.22 s; expert 10 steps at 0.2 GB FP16 weights per step over about 25 GB/s gives at least 0.08 s, up to about 0.5 s with graph-split overhead (assumed).

| Cameras | Estimated chunk latency | 30 Hz chunk (1.67 s) | Comment |
|---|---|---|---|
| 1 | about 1.0–1.4 s | supplies actions, borderline | discarding stale actions needs under 0.83 s: fails |
| 2 | about 1.9–2.3 s | starves | |
| 3 (released default) | about 2.8–3.2 s | starves | consistent with the reported 5.05 s given unknown overheads |

- The action-supply conditions are from [serving methods](serving-methods.md). Compared with the 0.11 s roofline for a generic 10-TFLOP/s device, the RK3588 estimate is 10–30× slower, from low NPU utilization and FP16 vision.

**Options, unproven on this hardware (hypotheses)**
1. One camera and a shared encoder result cached while the scene is static (as in [token pruning and caching](token-pruning-and-caching.md)).
2. Lower-resolution vision input or a smaller encoder, which needs fine-tuning because SmolVLA is trained at 512×512.
3. INT8 vision with outlier handling (input rescaling) after checking task success, not just cosine similarity.
4. Replace the flow expert with an ACT-style or regression head over cached VLM features, or run the VLM at low rate beside an ACT policy at control rate ([action representation and chunking](action-representation-and-chunking.md)).
5. Play chunks back slower than the training rate (15 Hz gives a 3.3 s chunk); this changes dynamics and was not tested in any source.

**Evidence quality:** Rockchip's numbers are first-party and reproducible; every VLA-specific number here is a single community README. No source reports task success for a policy running on the RK3588 NPU. [Embodied.cpp](../resources/embodied-cpp.md) names RK boards as a target but reports none.

## Open questions
- Per-module SmolVLA timings and camera count behind the 5049 ms figure; whether RKNN supports cross-attention with cached K/V and a 10-step loop without CPU fallback.
- Task success of INT8 and FP16 converted policies on real hardware.
- Behavior under thermal load and with camera, encoder and NPU sharing DRAM.
- Whether the three NPU cores can be scheduled to split one image's encoder (as the shard experiment did) without a custom runtime.

See also: [robot compute partitioning](robot-compute-partitioning.md) for how commercial robots use the RK3588 alongside Jetson modules.
