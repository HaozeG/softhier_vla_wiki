---
type: concept
tags: [quantization, int4, ternary, ptq, qat, w4a8, memory-bound]
sources: [resources/models/openvla.md, resources/compression/bitvla.md, resources/compression/quantvla.md, resources/serving/vla-cpp.md, resources/serving/vla-simd.md, resources/serving/vla-xpu-characterization.md, resources/compression/deer-vla.md, resources/serving/realtime-vla.md, resources/surveys/survey-efficient-vla-guan.md]
---
# Quantization for VLAs

## Summary
(Format names such as W4A8, PTQ and ternary: [glossary, compression](../glossary/compression.md).)

Quantization reliably cuts VLA memory (2–11×), but wall-clock gains depend on the kernel and on whether the phase is memory- or compute-bound. Weight-only INT4 helped a 7B autoregressive VLA on GPUs; 8-bit was slower because of dequantization overhead; GGUF 4-bit gave only 1.1× on GR00T-N1.7. The flow/diffusion action head is the most error-sensitive part, so low-bit LLM plus higher-precision expert (or expert MLPs only) is the safe default. Native low-bit training (BitVLA) gives the largest gains but requires a specialised kernel.

```text
WHERE EACH PART TOLERATES QUANTIZATION (as the sources report)
+------------------+
| vision encoder   |  kept at 16 bit in Rockchip's NPU ports; one low-bit
|                  |  encoder (BitVLA) needed QAT + distillation
+------------------+
  |
  v visual tokens
+------------------+
| LLM              |  low bit works: 4-bit weights, or W4A8 with
|                  |  calibration
+------------------+
  |
  v prefix keys + values
+------------------+
| action expert    |  most error-sensitive: attention projections or
| (flow / DiT)     |  the whole DiT collapsed accuracy; MLPs only
|                  |  stayed near baseline; errors build up over steps
+------------------+

QAT = quantization-aware training; W4A8 = 4-bit weights, 8-bit activations
```

```text
WHEN A SMALLER FORMAT BECOMES FASTER (reported cases)

case                        reported effect on speed
memory                      always shrinks (2-11x)
native low-bit kernel       faster: tensor-core ternary about 4x
dequantize to bf16 first    little: GGUF 4-bit about 1.1x; 8-bit slower
native int8 path            faster on CPUs (W8A8 1.13-2.7x); slower on one M4
```
The first drawing is "Where to quantize" under Lessons and the second is "Speed needs a kernel".

## Details
**Evidence by method**

| Method                                                         | Result                                                                                                           | Hardware                           | Source                                                  |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------- |
| OpenVLA bf16 / int8 / int4 (weights)                           | success 71.3 / 58.1 / 71.9%; memory 16.8 / 10.2 / 7.0 GB                                                         | A5000 (eval), various GPUs         | [OpenVLA](../resources/models/openvla.md)               |
| OpenVLA 4-bit vs bf16                                          | 1.14× faster, LIBERO average 76.5 → 67.7                                                                         | GPU not stated in the text read    | [XPU](../resources/serving/vla-xpu-characterization.md) |
| BitVLA (ternary weights, INT8 activations, QAT + distillation) | LIBERO 96.0% at 1.4 GB vs OpenVLA-OFT 97.1% at 15.4 GB; 73 ms vs 321 ms on A100 (baseline copied from OFT paper) | A100                               | [BitVLA](../resources/compression/bitvla.md)            |
| BitVLA tensor-core kernel                                      | 4.57× / 4.02× faster than CUDA-core path; packing alone no latency change                                        | RTX 3060 / AGX Orin                | [vla.cpp](../resources/serving/vla-cpp.md)              |
| QuantVLA W4A8 (LLM + DiT MLP, calibrated)                      | π0.5 97.1 → 97.6% LIBERO, memory 4.27 → 1.28 GB; GR00T N1.5 86.5 → 88.0%                                         | A100 (no latency reported)         | [QuantVLA](../resources/compression/quantvla.md)        |
| GGUF Q4_0 (+ vision) on GR00T-N1.7                             | 190–195 vs 196/200 successes; 1.14× faster; file 6.3 → 4.6 GB                                                    | RTX 3060                           | [vla.cpp](../resources/serving/vla-cpp.md)              |
| W8A8 on CPUs                                                   | 1.13–1.26× on desktop CPUs, 1.7–2.7× on Pi 5, slower on M4 for some policies                                     | four CPUs                          | [vla.simd](../resources/serving/vla-simd.md)            |
| DeeR-VLA LLM precision                                         | fp32 6 GB / fp16 3 GB / int4 1.7 GB; success length 4.13 / 4.12 / 3.91                                           | hardware not stated for this table | [DeeR-VLA](../resources/compression/deer-vla.md)        |

**Lessons**
- **Speed needs a kernel.** OpenVLA's 8-bit run dropped to about 1.2 Hz on an A5000 and the success drop was attributed to the resulting slower control rate, not to token accuracy; 4-bit was faster because reduced memory traffic outweighed dequantization cost ([OpenVLA](../resources/models/openvla.md)). Packed low-bit weights alone leave latency unchanged; tensor-core ternary execution gave 4× ([vla.cpp](../resources/serving/vla-cpp.md)).
- **Vision encoder.** Rockchip's NPU ports keep the encoder at 16 bit ([toolchain](../resources/rk3588/rockchip-rknn-rkllm-toolchain.md)), and BitVLA's low-bit encoder needed quantization-aware training and distillation ([BitVLA](../resources/compression/bitvla.md)).
- **Where to quantize.** In π0.5 and GR00T N1.5, quantizing the DiT's attention projections or the whole DiT collapsed accuracy (π0.5 71.6% for DiT only; 76.3% for LLM + full DiT) while LLM + DiT MLP stayed near baseline (95.4%, and 97.6% with calibration) ([QuantVLA](../resources/compression/quantvla.md)). Small errors accumulate over the flow steps.
- **Task success is not predicted by action error.** In vla.cpp, Q4_0 had larger fixed-input error than Q8_0 yet similar success, and a one-step solver with a 0.93 action difference still scored 99/100 ([vla.cpp](../resources/serving/vla-cpp.md)); conversely a precision error in SmolVLA's positional-index computation dropped a LIBERO task from 9/10 to 2/10. Validate with rollouts and validate discrete preprocessing.
- **Interactions:** 4-bit quantization reduces speculative-decoding acceptance and combined methods lost more accuracy than either alone on OpenVLA (spec + cache 68.5%, quant + cache 65.1%) ([XPU](../resources/serving/vla-xpu-characterization.md)).
- **PTQ versus QAT:** post-training 1-bit conversion of a full-precision backbone is not expected to work; BitVLA needed a native 1-bit LLM and quantization-aware distillation for the vision encoder, and 7 + 14 days of H800 training ([BitVLA](../resources/compression/bitvla.md)).
- **Low-bit is a hardware feature.** Ternary × INT8 turns multiplies into integer adds; the authors argue for dedicated accelerators but no energy measurement exists ([BitVLA](../resources/compression/bitvla.md)). Realtime-VLA lists INT8 as future work for compute-bound encoding ([Realtime-VLA](../resources/serving/realtime-vla.md)).
- **Surveys** cite SQIL (state-importance-guided QAT) and PTQ variants but no comparison table ([Guan et al.](../resources/surveys/survey-efficient-vla-guan.md)).

**Why bits and speed are different things.** Lower-bit weights cut the bytes read each time they are used, and that helps only where the kernel keeps the saving: OpenVLA's int4 ran faster because the reduced memory traffic outweighed the dequantization cost, while its int8 run was slower because of dequantization overhead ([OpenVLA](../resources/models/openvla.md)); BitVLA's packed ternary weights alone left latency unchanged until a tensor-core kernel was used ([vla.cpp](../resources/serving/vla-cpp.md), [BitVLA](../resources/compression/bitvla.md)). **See also:** [technique comparison](technique-comparison.md) puts these results next to the other techniques; the phases and which of them are limited by memory are in the [workload note](inference-workload-characterization.md).

## Open questions
- Quantized SmolVLA or π0.5 task success on real hardware with a native INT8 or INT4 datapath; most results are LIBERO simulation.
- Whether a low-bit flow expert is viable when activation precision is also reduced (QuantVLA tested W4A4 only on π0.5 LIBERO: 95.3%).
