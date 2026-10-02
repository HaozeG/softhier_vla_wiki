---
type: entity
tags: [rk3588, rkllm, vlm, llm, measurements, first-party, community]
sources: [https://github.com/airockchip/rknn-llm, https://docs.radxa.com/en/rock5/rock5b/app-development/ai/rkllm-qwen2-vl, https://github.com/Qengineering/Qwen3-VL-2B-NPU]
---
# RK3588 NPU: measured LLM and VLM numbers

## Summary
Rockchip publishes RKLLM benchmarks for language models and a few vision-language models on RK3588, and community ports (Radxa, Qengineering) add reproducible VLM runs. These are the only quantitative NPU numbers for transformer workloads on the RK3588 in this wiki. They show two regularities: decode runs at about 24–30 GB/s of implied weight traffic (memory-bound), and prefill reaches only about 12–19% of the 6 TOPS headline. The SmolVLM-256M row is the closest published proxy for SmolVLA's vision and language trunk.

## Details
**Rockchip benchmark (RK3588, w8a8, 128-token prompt, 64 new tokens; columns TTFT ms / tokens per s / memory MB)**

| Model          | TTFT (ms) | Tokens/s | Memory (MB) |
| -------------- | --------- | -------- | ----------- |
| Qwen2 0.5B     | 145.90    | 41.58    | 669.56      |
| MiniCPM4 0.5B  | 135.29    | 45.34    | 534.82      |
| TinyLlama 1.1B | 243.93    | 24.43    | 1093.66     |
| Qwen2.5 1.5B   | 378.31    | 16.69    | 1689.21     |
| Gemma2 2B      | 598.41    | 10.37    | 2779.22     |
| Phi3 3.8B      | 1017.28   | 7.45     | 3758.34     |
| ChatGLM3 6B    | 1352.94   | 4.98     | 5985.99     |
| LFM2.5-VL 450M | 102.74    | 62.16    | 436.94      |

**Rockchip multimodal rows (RK3588, w8a8 language model)**

| Model         | Image encoder     | Prefill               | Decode         |
| ------------- | ----------------- | --------------------- | -------------- |
| SmolVLM-256M  | 842 ms at 512×512 | 77.3 ms (128 tokens)  | 78 tokens/s    |
| Qwen3.5-0.8B  | 690 ms at 448×448 | 1.56 s (216 tokens)   | 27 tokens/s    |
| Qwen2-VL-2B   | 3.28 s at 392×392 | 632.6 ms (196 tokens) | 16.6 tokens/s  |
| Qwen3-VL-2B   | 2.08 s at 448×448 | 649 ms (196 tokens)   | 14.91 tokens/s |
| Qwen2.5-VL-3B | 2.93 s at 392×392 | 1120 ms (196 tokens)  | 8.66 tokens/s  |

**Community runs**
- Radxa Qwen2-VL-2B (RKLLM 1.2.3, driver 0.9.8): vision encoder RKNN FP16 at 392×392 giving 196×1536 features; LLM W8A8; prefill 222 tokens in 929.4 ms (238.9 tokens/s); decode 60 tokens in 3897 ms (15.39 tokens/s); vision model load 2.36 s and LLM load 3.05 s.
- Qengineering Qwen3-VL-2B on Rock 5C and Orange Pi 5: 11.5 tokens/s overall; vision encoder FP16 at 448×448 takes 0.9 s warm and 10.0 s cold (first load from disk); 3.1 GB total memory; LLM w8a8.
- A third-party expectation of about 10–15 tokens/s for 1.1B models (tinycomputers) is consistent with the table above.

**Derived cross-checks (my arithmetic; parameter counts are the nominal sizes in the model names)**
- Decode: memory column × tokens/s gives 24–30 GB/s across nine models (for example Qwen2 0.5B 27.8, Qwen2.5 1.5B 28.2, ChatGLM3 6B 29.8), so decode is memory-bound near the SoC's practical DRAM bandwidth (CPU STREAM in [platform note](rk3588-platform-specs.md): 21–22 GB/s). Memory includes KV cache and embeddings, so this is an upper estimate of weight traffic.
- Prefill: 128 tokens × 2 × parameters ÷ TTFT gives 0.73–1.15 TFLOP/s, about 12–19% of the 6 TOPS headline.
- Vision encoder: SmolVLM-256M's 842 ms for a 512×512 image is about 0.25 TFLOP/s if the tower is a 12-layer, 768-wide SigLIP-base (about 213 GFLOP; layer count assumed), about 4% of 6 TOPS. Its config matches SmolVLA's backbone in width, heads, patch size and resolution (hidden 768, 12 heads, patch 16, 512); the 500M backbone's config marks `use_base_siglip` false, so the depth may differ.

**Caveats:** the Rockchip tables are first-party and were measured at maximum clocks; the fetched page gave the column header but not the RKLLM version for the LLM table; community numbers are single runs on unspecified boards and thermal states.

See also: [Rockchip toolchain](rockchip-rknn-rkllm-toolchain.md), [platform specs](rk3588-platform-specs.md), [RK3588 robot-policy reports](rk3588-robot-policy-reports.md).
