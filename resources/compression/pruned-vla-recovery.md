---
type: paper
tags: [structured-pruning, width-pruning, distillation, openvla-oft, cogact, jetson-thor, recent]
sources: [arxiv:2609.19579, https://arxiv.org/abs/2609.19579]
---
# Recovering Aggressively Pruned Vision-Language-Action Models with Offline Hidden-State Distillation

Kim, Choi, Lee (Chung-Ang University), arXiv 2609.19579 (Sept 2026). Posted Sept 2026 with few reviews; results are internally consistent but not yet independently reproduced.

## Summary
The paper prunes the Llama-2 7B backbone of OpenVLA-OFT and CogACT by width (attention heads and MLP channels, keeping the residual width) and recovers accuracy offline from a cache of teacher hidden states, without reinforcement learning or rollouts. It sweeps nine compression ratios and compares width to depth pruning under one protocol.

## Key claims
- **Failure without recovery (§I, §V-A):** removing 63% of OpenVLA-OFT's backbone drops LIBERO-Long success from 93.2% to 0.8%; no success at 72%.
- **Method (§III):** action-path first-order Taylor importance (gradient through the inference action head), width pruning that leaves teacher and student hidden shapes equal so an MSE hidden-state loss needs no projector; teacher hidden states cached in one pass; LoRA rank 32 on the backbone and vision path.
- **Recovery cost and result:** 63% reduction recovers to 89.7 ± 2.4% (teacher 93.2%) in about 8 H100 GPU-hours. The prior RL-based recovery (RLRC) reports about 320 GPU-hours with a simulator in the loop.
- **When distillation matters (§V-B):** up to about 45% reduction plain supervised recovery is as good; beyond 63% hidden-state distillation adds +2.1 to +4.5 points on OpenVLA-OFT and +9.4 to +22.1 on CogACT.
- **Width vs depth (Fig. 4, §V-D):** at matched effective reduction width pruning gives higher success (margin 2.8–12.9 points on OpenVLA-OFT, 9.0–33.2 on CogACT) but depth pruning is faster (1.31–1.66× vs 1.14–1.18× on an H100 workstation).
- **Latency floors (Table II):** CogACT latency 129.1 ms → 85.0 ms at 72% reduction and then flat because ten DDIM action-head steps are a fixed cost; OpenVLA-OFT 59.3 → 50.4 ms at 81% because the layer count is unchanged. Memory tracks parameters (CogACT 14.7 → 5.6 GiB).
- **Real robot (Table III, AgileX PiPER, on-board Jetson Thor):** 72% width-pruned student with distillation 77.5% success vs teacher 65.5% vs supervised-only recovery 59.5%; latency 362 → 162 ms (2.23×), memory 15.0 → 5.7 GiB. The speedup on the robot is about twice the workstation's, which the authors attribute to the bandwidth-limited device benefiting more from smaller weights.
- **Limitations (§VII):** compression ratios swept only in simulation; both backbones are Prismatic-family; fixed cached observations.

## Related
See also: [CLP](clp-layer-pruning.md), [EfficientVLA](efficientvla.md), [OpenVLA-OFT](../models/openvla-oft.md).
