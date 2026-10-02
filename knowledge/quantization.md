---
type: concept
tags: [quantization, int4, ternary, ptq, qat, w4a8, memory-bound]
sources: [resources/models/openvla.md, resources/compression/bitvla.md, resources/compression/quantvla.md, resources/serving/vla-cpp.md, resources/serving/vla-simd.md, resources/serving/vla-xpu-characterization.md, resources/compression/deer-vla.md, resources/serving/realtime-vla.md, resources/surveys/survey-efficient-vla-guan.md]
---
# Quantization for VLAs

## Summary
Quantization reliably cuts VLA memory (2–11×), but wall-clock gains depend on the kernel and on whether the phase is memory- or compute-bound. Weight-only INT4 helped a 7B autoregressive VLA on GPUs; 8-bit was slower because of dequantization overhead; GGUF 4-bit gave only 1.1× on GR00T-N1.7. The flow/diffusion action head is the most error-sensitive part, so low-bit LLM plus higher-precision expert (or expert MLPs only) is the safe default. Native low-bit training (BitVLA) gives the largest gains but requires a specialised kernel.

```text
WHERE TO QUANTIZE (what each part tolerates)
+----------------------------+    FP16 in RK3588 ports;
| vision encoder             |    BitVLA needed QAT + distillation
+----------------------------+
      |  visual tokens
      v
+----------------------------+    low-bit works: INT4 weights,
| LLM                        |    or W4A8 with calibration
+----------------------------+
      |  prefix features
      v
+----------------------------+    most error-sensitive: quantizing the
| action expert              |    attention projections or the whole DiT
| (flow / DiT)               |    collapsed accuracy; MLPs only stayed near
|                            |    baseline; errors accumulate over the
+----------------------------+    flow steps

does a smaller format make it faster?
  memory always shrinks (2-11x)
  native low-bit kernel (tensor-core ternary: ~4x)   -> yes
  dequantize to bf16 first (8-bit: slower; GGUF 4-bit: 1.1x) -> little or none
  native int8 path (W8A8 on CPUs: 1.1-2.7x; slower on M4 for some policies)
  compute-bound phase (vision, prefill)  -> weight-only helps less
  memory-bound phase (expert loop)       -> helps most, yet it is the phase
                                            most sensitive to error (inference)
```

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
- **Where to quantize.** In π0.5 and GR00T N1.5, quantizing the DiT's attention projections or the whole DiT collapsed accuracy (π0.5 71.6% for DiT only; 76.3% for LLM + full DiT) while LLM + DiT MLP stayed near baseline (95.4%, and 97.6% with calibration) ([QuantVLA](../resources/compression/quantvla.md)). Small errors accumulate over the flow steps.
- **Tension (inference).** Weight-only quantization helps the memory-bound expert loop most ([inference workload characterization](inference-workload-characterization.md)), yet the expert is the part QuantVLA found most sensitive; so the usual split is low-bit LLM, higher-precision expert attention, and low-bit expert MLPs only after calibration.
- **Task success is not predicted by action error.** In vla.cpp, Q4_0 had larger fixed-input error than Q8_0 yet similar success, and a one-step solver with a 0.93 action difference still scored 99/100 ([vla.cpp](../resources/serving/vla-cpp.md)); conversely a precision error in SmolVLA's positional-index computation dropped a LIBERO task from 9/10 to 2/10. Validate with rollouts and validate discrete preprocessing.
- **Interactions:** 4-bit quantization reduces speculative-decoding acceptance and combined methods lost more accuracy than either alone on OpenVLA (spec + cache 68.5%, quant + cache 65.1%) ([XPU](../resources/serving/vla-xpu-characterization.md)).
- **PTQ versus QAT:** post-training 1-bit conversion of a full-precision backbone is not expected to work; BitVLA needed a native 1-bit LLM and quantization-aware distillation for the vision encoder, and 7 + 14 days of H800 training ([BitVLA](../resources/compression/bitvla.md)).
- **Low-bit is a hardware feature.** Ternary × INT8 turns multiplies into integer adds; the authors argue for dedicated accelerators but no energy measurement exists ([BitVLA](../resources/compression/bitvla.md)). Realtime-VLA lists INT8 as future work for compute-bound encoding ([Realtime-VLA](../resources/serving/realtime-vla.md)).
- **Surveys** cite SQIL (state-importance-guided QAT) and PTQ variants but no comparison table ([Guan et al.](../resources/surveys/survey-efficient-vla-guan.md)).

**See also:** [inference workload characterization](inference-workload-characterization.md) explains why weight-only quantization helps memory-bound phases (expert loop) more than compute-bound ones; [technique comparison](technique-comparison.md) puts these results next to the other techniques.

## Open questions
- Quantized SmolVLA or π0.5 task success on real hardware with a native INT8 or INT4 datapath; most results are LIBERO simulation.
- Whether a low-bit flow expert is viable when activation precision is also reduced (QuantVLA tested W4A4 only on π0.5 LIBERO: 95.3%).
