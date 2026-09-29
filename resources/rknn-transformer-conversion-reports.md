---
type: entity
tags: [rk3588, rknn, transformer, int8, siglip, community, low-evidence]
sources: [https://amohan.dev/blog/2025/shard-optimizing-vision-transformers-edge-npu/, https://github.com/airockchip/rknn-toolkit2/issues/460, https://github.com/airockchip/rknn_model_zoo/issues/454]
---
# RKNN reports on converting transformers (SigLIP, ViT) for the RK3588 NPU

## Summary
Community reports show that vision transformers are the fragile part of a VLA on the RK3588: a SigLIP encoder failed to compile until it was manually tiled and sharded, INT8 quantization failed on its activation outliers until inputs were rescaled, and a ViT tracker converted without error but gave wrong outputs after operator fusion. CNN detectors, by contrast, quantize with small losses. All are single-author or user-issue reports, not vendor documentation.

## Details
- **SigLIP on the NPU (a blog by one engineer):** the model's 1024-token activations reached about 25 MB per matrix while the author found a per-tensor limit of 32 KB in the NPU's scratchpad (tensors up to 32 KB worked and 32.1 KB crashed), giving compiler error `0xe010` (REGTASK overflow). The workaround was manual 32×32 tiling of attention, a dummy non-linear op inserted to stop the compiler re-fusing tiles, and cutting the graph into 26 binary shards run round-robin across three NPU cores. Latency fell from about 30 s to under 1.8 s (15×). The author's limit is an observation about the toolchain, not a Rockchip specification; Turing Pi lists 1 MB of shared on-chip NPU memory ([platform note](rk3588-platform-specs.md)).
- **INT8 outliers in SigLIP:** activation spikes of about 300 beside signal values of about 0.05 could not share one INT8 scale; multiplying inputs by 0.1, running, then scaling the outputs by 10 raised agreement with FP32 from 0.02 to 0.999 (the metric is the author's; no task accuracy).
- **Silent wrong outputs (rknn-toolkit2 issue 460):** a ViT-based tracker converted on RK3588 with toolkit 2.3.2 at FP16 (203 ONNX operators reduced to 83 RKNN operators, including 12 fused scaled-dot-product attention and 14 fused norm operators) produced degraded results versus the ONNX model; the reporter suspected FP16 rounding in fused Erf/Softmax/ReduceMean/Pow/Sqrt. No maintainer response was recorded.
- **CNN contrast (rknn_model_zoo issue 454, community benchmark on a Vicharak Axon RK3588):** YOLOv8n INT8 with three cores runs 199 / 330 / 649 FPS at 640 / 480 / 320 input; INT8 costs 0.5–1.5 mAP against FP32 on CPU (for example YOLOv8n 35.9 vs 37.3 at 640), with zero-copy input and hardware decode and resize.
- **Related pitfalls from the SO-ARM101 ACT port:** LayerNorm-fusion crashes and silent input reordering ([robot-policy reports](rk3588-robot-policy-reports.md)).
- **Relevance:** SmolVLA's vision tower is a SigLIP; the fp16 vision path used by Rockchip and community VLM ports ([measurements](rk3588-vlm-llm-measurements.md)) avoids the INT8 outlier problem at the cost of speed. Validate every converted graph against ONNX Runtime before trusting latency.
- **Trust level:** low; single engineer's blog and user-filed issues.

See also: [Rockchip toolchain](rockchip-rknn-rkllm-toolchain.md), [RK3588 deployment note](../knowledge/rk3588-vla-deployment.md).
