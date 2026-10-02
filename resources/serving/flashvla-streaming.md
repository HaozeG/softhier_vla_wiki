---
type: paper
tags: [flow-matching, streaming-decoding, async-inference, pi0.5, smolvla, recent]
sources: [arxiv:2608.27384, https://arxiv.org/abs/2608.27384, https://github.com/z-lab/flashvla]
---
# FlashVLA: Streaming Action Decoding for Fast and Asynchronous VLA Inference

Li, Tang, Liu (UC San Diego, MIT), arXiv 2608.27384 (Aug 2026). Recent paper. Not the same work as the SVD-based token-pruning "FlashVLA" described in [Guan et al.](../surveys/survey-efficient-vla-guan.md) or the action-reuse "FlashVLA" in [Yu et al.](../surveys/survey-efficient-vla-yu.md).

## Summary
FlashVLA changes how a flow-matching action expert is run: instead of ten denoising steps on one chunk, it keeps a buffer of N chunks at staggered noise levels and advances all of them one step per forward pass under chunk-wise causal attention, so one executable chunk emerges per pass. This cuts per-invocation latency and also gives smooth asynchronous execution without a future-state predictor. It needs a fine-tuning pass (multi-buffer joint fine-tuning).

## Key claims
- **Profile (Fig. 1b):** on π0.5 (RTX 4090, two views, no system optimization), action decoding is about 75% of per-invocation time because of the ten denoising steps.
- **Method (§3):** buffer of N (default 4) chunks with staggered noise levels; chunk-wise causal mask (noisier chunks attend to cleaner ones); cold start needs N − 1 warm-up passes per episode; FiLM-based timestep conditioning in the expert; CUDA graphs, linear-layer packing and max-autotune compile.
- **LIBERO async (Table 1, d=1):** π0.5 96.9% avg success, 53.8 ms per step. FlashVLA 97.8%, 22.1 ms (2.43×). VLASH 97.2%, 46.8 ms (1.15×); StreamingVLA 94.9%, 31.6 ms (1.70×).
- **Latency (Table 2, per invocation):** π0.5 with CUDA graphs and fusion: RTX 4090 45.8 ms (2 views) / 55.4 ms (3 views) → FlashVLA 26.7 / 36.8 ms; RTX 5090 37.0 / 44.8 → 20.3 / 27.1 ms. Realtime-VLA: 29.2 / 38.9 ms on RTX 4090.
- **Up to 20× claim:** per-step action-decoding latency; the paper attributes 9.3× to reduced GPU work and the rest to removing kernel-launch serialization (footnote 1).
- **Other architectures (Table 5):** SmolVLA (LIBERO) latency 19.7 → 10.1 ms with success 80.1% → 80.1%; LingBot-VLA 70.6 → 25.1 ms with success +3.4 points.
- **Long-horizon effect:** on RoboTwin 2.0 long tasks success rises 53.0 → 89.6% (synchronous); the authors attribute this to implicit chunk-level memory in the buffer, not shown independently.
- **Real robot:** Franka with an RTX A4000: 67.3 ms latency, 30 Hz control with two-step asynchronous delay; average task score 84.4% vs 80.0% for synchronous π0.5.
- **Limitations:** requires fine-tuning; inherits the independent-chunk pretraining objective; cold-start overhead per episode.

## Related
See also: [RTC](real-time-chunking.md), [Realtime-VLA](realtime-vla.md), [Jetson-PI](jetson-pi.md), [OpenVLA-OFT](../models/openvla-oft.md).
