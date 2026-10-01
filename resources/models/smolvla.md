---
type: paper
tags: [vla, smolvla, edge, flow-matching, layer-skipping, async-inference]
sources: [arxiv:2506.01844, https://arxiv.org/abs/2506.01844, https://huggingface.co/blog/smolvla]
---
# SmolVLA: A vision-language-action model for affordable and efficient robotics

Shukor, Aubakirova, Capuano, et al. (Hugging Face, Sorbonne, valeo.ai), arXiv 2506.01844 (June 2025). Open weights, code and data via LeRobot.

## Summary
SmolVLA is a 450M-parameter VLA: a truncated SmolVLM-2 backbone plus a roughly 100M-parameter flow-matching action expert. It targets training on one GPU and deployment on consumer GPUs or CPUs. Efficiency comes from four design choices: skipping upper VLM layers, only 64 visual tokens per frame, a small pretrained VLM, and interleaved cross-/self-attention in the action expert. The paper also introduces an asynchronous inference stack that decouples action execution from chunk prediction. It is pretrained on fewer than 30k community-collected episodes from low-cost SO100 arms.

## Key claims
- **Architecture (§3.1, §4.3):** SmolVLM-2 (SigLIP encoder + SmolLM2 decoder) as backbone; the action expert reads features from the first N = L/2 LLM layers (16 layers in the released model); total 450M parameters, about 100M in the action expert. The survey [Guan et al.](../surveys/survey-efficient-vla-guan.md) lists SmolVLM-2 sizes of 0.24B / 0.45B / 2.25B.
- **Visual tokens (§3.1):** no image tiling; global image only plus pixel shuffle, giving 64 visual tokens per frame. Training images are resized to 512×512.
- **Sensorimotor state:** projected to a single token and fed into the VLM prefix. Feeding state to the VLM beats feeding it to the expert (Table 11: CA 80.3 vs 73.3 on LIBERO).
- **Action expert (§3.1):** conditional flow-matching transformer with alternating cross-attention (to VLM keys/values) and causal self-attention blocks. Hidden size is 0.75× the VLM width. Action chunk n = 50 and 10 flow steps at inference (§4.3).
- **Simulation results by size (Table 2, multi-task, no robot pretraining):** LIBERO average SmolVLA 0.24B 82.75, 0.45B 87.3, 2.25B 88.75 (π0 3.3B pretrained 86.0; π0 initialized from PaliGemma 71.8; OpenVLA 76.5; Octo 75.1). Meta-World average 56.95 / 57.3 / 68.24 (π0 47.9 pretrained, 50.5 PaliGemma-initialized). Real-world results (Tables 3–5) are for the 0.45B model only. Papers that quote 88.8 for SmolVLA are citing the 2.25B variant.
- **Ablations (LIBERO, from-scratch expert, VLM frozen):**
  - CA+SA interleaved 85.5 avg vs CA 79.0 vs SA 74.5 (Table 6).
  - Causal 74.5 vs bidirectional 67.5 on the expert's action tokens (Table 7).
  - Using the first N layers: N=8 75.0, N=16 78.5, N=24 79.5, N=32 80.3 (Table 8). Skipping layers of a 500M VLM beats using a 256M VLM (75.8).
  - Expert width ×1.0 / ×0.75 / ×0.5 / ×0.25 = 82.3 / 77.5 / 80.3 / 73.8 (Table 9; rows are noisy and non-monotonic).
  - Chunk size 1 → 50.0, 10 → 84.0, 50 → 80.3, 100 → 74.5 (Table 12).
- **Pretraining data (§3.2, Table 1):** 481 community datasets, 22.9K episodes, 10.6M frames (the Hugging Face blog says 487 datasets and about 10M frames; the paper's Table 1 is the more specific figure). Task text was re-annotated with Qwen2.5-VL-3B-Instruct and camera views were renamed to a standard order.
- **Compute (§4.3):** about 30k GPU hours for the whole project; pretraining used 4 GPUs but fits on one. Compared with π0 (3.3B), SmolVLA is about 40% faster to train and uses 6× less memory (§4.5). Training used bf16 and `torch.compile`.
- **Real-world results (Table 5, SO100):** pretrained multi-task 78.3% avg vs non-pretrained multi-task 51.7% vs single-task 40%.
- **Async inference (§3.3, §4.6, Algorithm 1):** a RobotClient sends an observation to a (possibly remote) PolicyServer when the action queue falls below a fraction g of the chunk. Near-duplicate observations are filtered in joint space. Overlapping chunks are aggregated. An idle queue is avoided when g ≥ (E[ℓ_S]/Δt)/n, with Δt = 33 ms at 30 fps. Sync vs async on real tasks: avg success 78.3 vs 73.3 (sorting fell 70 → 50); task time 13.75 s vs 9.7 s (about 30% faster); 9 vs 19 cubes in a fixed time.
- **Not reported in the text read:** absolute on-device latency, Hz or power. The "runs on CPU/consumer GPU/MacBook" claim is qualitative; see [SmolVLA entity](../../knowledge/smolvla.md) for what can be derived.
- **Limitations (§5.1):** pretraining data is a single robot type (SO100); no long-horizon reasoning; dataset diversity; the VLM backbone was pretrained mainly on document and OCR tasks, and its suitability for robotics is untested.
- **Released config (first-party, `lerobot/smolvla_base`):** backbone `SmolVLM2-500M-Video-Instruct`, `num_vlm_layers` 16, three cameras resized with padding to 512×512, language padded to 48 tokens, chunk 50, 10 steps, expert width multiplier 0.75; used in [edge budget estimate](../../knowledge/edge-budget-estimate.md).

## Relevance to SoftHier-VLA
SmolVLA is the reference small VLA for this wiki: its layer counts, token counts, expert size and 10 flow steps give the inputs for the FLOP estimate in [edge-budget-estimate](../../knowledge/edge-budget-estimate.md). Its layer skipping motivates [layer skipping and pruning](../../knowledge/layer-skipping-and-pruning.md); its async stack is a serving method in [serving methods](../../knowledge/serving-methods.md).

See also: [FlashVLA](../serving/flashvla-streaming.md) and [CLP](../compression/clp-layer-pruning.md) (applied to SmolVLA), [vla.cpp](../serving/vla-cpp.md) and [vla.simd](../serving/vla-simd.md) (measured latencies), [OpenVLA](openvla.md) and [π0](pi0.md) (baselines), [LeRobot async docs](../serving/lerobot-async-inference-docs.md).
