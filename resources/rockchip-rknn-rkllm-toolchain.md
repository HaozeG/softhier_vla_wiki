---
type: entity
tags: [rk3588, rockchip, rknn, rkllm, toolchain, first-party]
sources: [https://github.com/airockchip/rknn-llm, https://github.com/airockchip/rknn-toolkit2, https://github.com/airockchip/rknn_model_zoo, https://github.com/Qengineering/Qwen3-VL-2B-NPU]
---
# Rockchip RKNN, RKLLM and the RKNN model zoo

## Summary
Rockchip's NPU software is two toolchains: RKNN-Toolkit2 (converts ONNX and other graphs to `.rknn` for CNN and vision models) and RKLLM (converts Hugging Face language models to `.rkllm`). A multimodal model is split across them: the vision encoder goes through RKNN and only the language model goes through RKLLM. On RK3588 the released benchmarks use W8A8 for the language model and FP16 for the vision encoder. This note records what the first-party repositories state; measured numbers are in [RK3588 VLM/LLM measurements](rk3588-vlm-llm-measurements.md).

## Details
- **RKLLM (rknn-llm, latest listed release v1.3.1):** platforms RK3588, RK3576, RK3562 and RV1126B; language models include Qwen2/2.5/3/3.5, Llama-family, TinyLlama, Phi, ChatGLM3, Gemma 2/3/4 and InternLM2; multimodal models include Qwen2-VL and Qwen3-VL, MiniCPM-V-2.6, InternVL2/3-1B and SmolVLM/SmolLM3; also DeepSeek-R1-Distill, Janus-Pro and DeepSeekOCR. "RKLLM currently only converts the language model part" (Radxa's guide), so a VLA-style policy head, cross-attention expert or flow loop is not covered by it.
- **Quantization:** the RK3588 rows in the official benchmark are all w8a8; RK3576 and RV1126B rows also show w4a16 and w4a16_g128. A third-party test states RK3588 supports W8A8 only ([platform note](rk3588-platform-specs.md)).
- **Version coupling:** "your rkllm model must match the library" (a runtime/model version mismatch caused BPE dictionary parsing failures); the Qwen3-VL-2B port needed rkllm-runtime 1.2.3 and RKNPU driver 0.9.8 ([Qengineering](rk3588-vlm-llm-measurements.md)). Benchmarks are run with `optimization_level` 0 at maximum CPU and NPU frequencies.
- **RKNN-Toolkit2 (v2.3.2):** supports RK3588, RK3576, RK3566/68, RK3562, RV1103/1106, RV1126B and RK2118; Python 3.6–3.12; the repository page shown did not list operator support, data types or dynamic-shape rules (see the operator reports in [RKNN transformer reports](rknn-transformer-conversion-reports.md)).
- **RKNN model zoo:** classification (MobileNet, ResNet), detection (YOLOv5–v11, YOLOX, YOLO-World), segmentation (DeepLabv3, MobileSAM), pose, OCR, CLIP, Lite-Transformer, and speech (Whisper, Wav2Vec2). Quantization is INT8 for most vision models and FP16 for speech. Sample RK3588 single-core INT8 rows: YOLOv5n 640×640 82.5 FPS, YOLOv8n 73.5 FPS, MobileNet-v2 450.7 FPS.
- **Not in these pages:** a documented operator-support matrix for transformer attention, cross-attention or flow-matching loops; no VLA in the model zoo.

See also: [RK3588 platform](rk3588-platform-specs.md), [RKNN transformer reports](rknn-transformer-conversion-reports.md).
