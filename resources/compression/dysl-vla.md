---
type: paper
tags: [layer-skipping, dynamic-inference, jetson-orin, openvla-oft, distillation]
sources: [arxiv:2602.22896, https://arxiv.org/abs/2602.22896, https://github.com/PKU-SEC-Lab/DYSL_VLA]
---
# DySL-VLA: Efficient VLA Inference via Dynamic-Static Layer-Skipping

Yang, Qi, Xie, Yu, Liu, Li (Peking University, SIAT), arXiv 2602.22896 (v3, Mar 2026).

## Summary
DySL-VLA keeps a small set of informative "static" LLM layers always on and lets lightweight controllers skip blocks of the remaining "dynamic" layers, with small adapters summarizing the skipped block. Skipping is restricted around important actions via a trajectory-continuity signal (pre-skip prediction plus post-skip verification). Only adapters and controllers are trained, by two-stage distillation.

## Key claims
- **Observations (§3.1):** layers differ in how much they change activations (cosine similarity analysis); skipping the informative ones hurts most. Success is sensitive to a few key actions (grasp, release). Per-layer controllers add serial latency and gain little when half the layers are active (Fig. 4).
- **Where time goes (§2):** the LLM backbone is 84.3% of OpenVLA latency and 75.4% of OpenVLA-OFT latency.
- **Mechanisms (§3.2–3.4):** static layers about 20% of the stack; adapters map from a dynamic layer to the next static layer; the skipping-allow point moves with action continuity C_t = −mean‖A_j − A_{j−1}‖ over the last k = 5 actions; stage 1 trains adapters to imitate the skipped layers, stage 2 trains controllers plus adapters with a skip-encouraging loss.
- **CALVIN (Table 2, RTX 4090):** RoboFlamingo 3B 51.0 ms → DySL-VLA 13.6 ms (3.75×) at average length 2.89 vs 2.92; DeeR-VLA 19.3 ms at 2.83. Fine-tuned parameters 14M vs DeeR's 1.2B (85.7× fewer).
- **LIBERO with OpenVLA-OFT 7B (Table 3):** avg success 97.1 → 96.5. A6000 latency 53.0 → 27.4 ms; Jetson Orin 676 → 345 ms (DeeR-VLA 495 ms, FlexiDepth 502 ms). With 8-action chunks the Orin control frequency reaches 23.2 Hz. The exact Orin variant is not specified in the text read.
- **Ablation (Table 4):** removing pre-skip prediction drops length 2.89 → 2.42; removing dynamic-static split gives 1.87 at 27.6 ms; removing two-stage distillation leaves controllers closed and latency at 74.0 ms.
- **Stated limitation:** OpenVLA-OFT has less redundancy, so speedup is 1.93–1.96× vs 3.75× on RoboFlamingo.

## Relevance to SoftHier-VLA
A dynamic-depth method with a measured Jetson Orin point. As with [DeeR-VLA](deer-vla.md), run-time control flow must be honoured by the mapping. Its finding that per-layer controllers add serial latency is a caution for dynamic schemes on statically scheduled hardware. See [layer skipping and pruning](../../knowledge/layer-skipping-and-pruning.md).

See also: [DeeR-VLA](deer-vla.md), [CLP](clp-layer-pruning.md), [Jetson-PI](../serving/jetson-pi.md) (same group).
