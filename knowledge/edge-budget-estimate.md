---
type: concept
tags: [estimate, smolvla, roofline, 10-tops, back-of-envelope, hypothesis]
sources: [resources/smolvla.md, resources/vla-xpu-characterization.md, resources/vla-perf.md, resources/realtime-vla.md, resources/vla-cpp.md, resources/vla-simd.md, https://huggingface.co/lerobot/smolvla_base/blob/main/config.json, https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct/blob/main/config.json]
---
# Edge budget estimate: SmolVLA on a ~10 TOPS device

## Summary
**This is an estimate, not a measurement.** A released-config SmolVLA call (3 cameras) costs about 0.8 TFLOP, dominated by the vision encoder (about 0.64 TFLOP), not the LLM or the action expert. On a device with 10 TFLOP/s and 51.2 GB/s the roofline lower bound is about 0.11 s per 50-action chunk (0.09 s with 2 cameras). Realistic software (4–9× above roofline in the sources) gives about 0.4–1 s, which still keeps a 30 Hz robot supplied with actions using chunking and asynchronous execution. Keeping the 100M-parameter expert resident on chip would cut the bound to about 0.08 s.

## Details
**Inputs and their sources**
- From the [SmolVLA paper](../resources/smolvla.md): about 450M parameters, about 100M in the flow expert; chunk n = 50; 10 flow steps; 64 visual tokens per frame.
- From the first-party configs (`lerobot/smolvla_base` and its backbone `SmolVLM2-500M-Video-Instruct`, read from the Hugging Face Hub): three 256×256 cameras resized with padding to 512×512; vision encoder hidden size 768, 12 heads, patch 16 → 1024 patches per image, pixel-shuffle factor 4 → 64 tokens; language padded to 48 tokens; one state token; LLM hidden 960, MLP 2560, 15 heads with 5 KV heads (head dim 64), of 32 layers only the first 16 used (`num_vlm_layers` 16); expert width multiplier 0.75, cross-attention with self-attention every second layer, 10 steps, chunk 50.
- Derived from the config: one LLM layer has about 9.8M parameters (attention 2.5M + gated MLP 7.4M), so 16 layers are about 157M; the token-embedding table (49,280 × 960, about 47M) is a lookup and not streamed per token; the connector is about 12M.
- **Assumption not in the fetched config:** vision-encoder layer count and MLP width. The estimate uses a SigLIP-base-class tower of about 85M parameters (12 layers, MLP 3072); check against the model card. The stand-in device is 10 TFLOP/s and 51.2 GB/s, the Ascend 310B numbers in [XPU characterization](../resources/vla-xpu-characterization.md), the only sub-20-TOPS part with a listed bandwidth.
- Not modeled: expert cross-attention K/V projection of the prefix (assumed cached once, as in [vla.cpp](../resources/vla-cpp.md)), softmax and normalization work, and sensor preprocessing.

**FLOPs per call**

| Part | Basis | 2 cameras | 3 cameras (default config) |
|---|---|---|---|
| Vision encoder | per camera: 2 × 85M × 1024 + attention 12 × 4 × 1024² × 768 + connector, about 214 GFLOP | 428 GFLOP | 643 GFLOP |
| LLM prefix (16 layers) | 2 × 157M × tokens (177 or 241) + attention | 58 GFLOP | 79 GFLOP |
| Action expert, 10 steps | 10 × 2 × 100M × 50 | 100 GFLOP | 100 GFLOP |
| Total | | about 586 GFLOP | about 822 GFLOP |

**Roofline time per chunk** (per phase max of FLOPs ÷ 10 TFLOP/s and weight bytes ÷ 51.2 GB/s; bf16 weights)
- 3 cameras: vision 64 ms (compute-bound), LLM 8 ms, expert 39 ms if its 0.2 GB of weights are re-read each of 10 steps (intensity 50 FLOP/byte against a ridge of about 195) → about **111 ms**. With the expert resident on chip (weights read once, so 10 ms): about **82 ms**.
- 2 cameras: about 88 ms streaming, 59 ms resident. INT8 weights halve expert bytes (about 68 ms with 2 cameras, 92 ms with 3) if the device has native INT8 compute.
- The ordering (prefill compute-bound, expert memory-bound) matches [VLA-Perf](../resources/vla-perf.md) and the measured phase splits.

**Realistic latency**
- A hand-tuned stack reached within 1.3–1.4× of roofline on an RTX 4090 ([Realtime-VLA](../resources/realtime-vla.md)); typical stacks sit 4–9× above ([inference workload characterization](inference-workload-characterization.md)). Applied to 111 ms: about 0.15 s to 1 s.
- Sanity checks: SmolVLA was measured at 358–457 ms per chunk on a Jetson Orin Nano with a general runtime, and about 0.8 s on AGX Orin in a PyTorch leaderboard run ([vla.cpp](../resources/vla-cpp.md), [XPU characterization](../resources/vla-xpu-characterization.md), read off a plot); an engine-level CPU port on a Raspberry Pi 5 took 8.2 s ([vla.simd](../resources/vla-simd.md)). Those devices have more nominal compute than 10 TOPS, so the estimate is plausible for a well-engineered stack and optimistic for a naive one.

**Does that keep the robot moving?**
- A 50-action chunk at 30 Hz lasts 1.67 s. SmolVLA's async condition is g ≥ (ℓ/Δt)/n: ℓ = 0.4 s gives g ≥ 0.24; 0.8 s gives 0.48; 1.5 s gives 0.9 ([SmolVLA](../resources/smolvla.md)).
- [vla.simd](../resources/vla-simd.md) conditions: continuous supply needs ⌈30·ℓ⌉ ≤ 50 (ℓ ≤ 1.67 s); discarding stale actions needs twice that within 50 (ℓ ≤ 0.83 s). So latencies up to about 0.8 s supply actions at 30 Hz; reactivity to new observations is bounded by ℓ ([serving methods](serving-methods.md)).

**A real 6-TOPS NPU:** the RK3588 uses only about 4–19% of its headline TOPS on measured transformer workloads and runs vision encoders in FP16; the SmolVLA estimate there is about 1.0–1.4 s (1 camera) to 2.8–3.2 s (3 cameras), an order of magnitude above this roofline ([RK3588 deployment](rk3588-vla-deployment.md)).

**Design hypotheses (not established by the sources)**
1. Holding the expert's weights on chip removes about a quarter of the roofline time (39 → 10 ms); on a tile-based chip with large aggregate SRAM this is the natural mapping.
2. Because the vision encoder (1024 patches × 3 cameras, no tiling) is about 80% of FLOPs, camera count, input resolution (256×256 inputs are padded up to 512×512 by the released config) and encoder precision matter more than the LLM's depth. Token reductions after the encoder ([token pruning and caching](token-pruning-and-caching.md)) do not reduce that cost.
3. Weight quantization mostly helps memory-bound phases and only with native low-bit datapaths ([quantization](quantization.md)).

## Open questions
- Encoder depth and MLP width of the released SmolVLM2 vision tower; the real utilization of a 10-TOPS NPU on cross-attention and small-M matmuls; and fixed overheads of an NPU runtime.
